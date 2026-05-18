/**
 * جلسه آزمون: تایمر، ذخیره خودکار، ناوبری سوالات
 */
(function () {
    'use strict';

    var cfg = window.QUIZ_SESSION;
    if (!cfg) return;

    var form = document.getElementById('quiz-form');
    var timerEl = document.getElementById('time-remaining');
    var timerWrap = document.getElementById('quiz-timer');
    var progressBar = document.getElementById('quiz-progress-bar');
    var progressText = document.getElementById('quiz-progress-text');
    var saveStatus = document.getElementById('quiz-save-status');
    var totalQuestions = cfg.totalQuestions || 0;
    var timeLeft = cfg.timeLeftSeconds || 0;
    var hasLimit = cfg.hasTimeLimit;
    var storageKey = 'quiz_draft_' + cfg.quizId + '_' + cfg.userQuizId;

    function faNum(n) {
        return Number(n).toLocaleString('fa-IR');
    }

    function updateProgress() {
        var answered = form.querySelectorAll('input[type="radio"]:checked').length;
        var pct = totalQuestions ? Math.round((answered / totalQuestions) * 100) : 0;
        if (progressBar) progressBar.style.width = pct + '%';
        if (progressText) progressText.textContent = faNum(answered) + ' از ' + faNum(totalQuestions) + ' سوال';
        document.querySelectorAll('.qe-nav-btn').forEach(function (btn) {
            var qid = btn.getAttribute('data-question-id');
            var checked = form.querySelector('input[name="q' + qid + '"]:checked');
            btn.classList.toggle('is-answered', !!checked);
        });
        return answered;
    }

    function setSaveStatus(state, msg) {
        if (!saveStatus) return;
        saveStatus.className = 'qe-save-label';
        if (state === 'saved') saveStatus.classList.add('is-saved');
        else if (state === 'saving') saveStatus.classList.add('is-saving');
        else if (state === 'error') saveStatus.classList.add('is-error');
        saveStatus.textContent = msg;
    }

    function saveToStorage(name, value) {
        try {
            var data = JSON.parse(localStorage.getItem(storageKey) || '{}');
            data[name] = value;
            localStorage.setItem(storageKey, JSON.stringify(data));
        } catch (e) { /* ignore */ }
    }

    function saveAnswer(questionId, choiceId) {
        setSaveStatus('saving', 'در حال ذخیره…');
        fetch(cfg.saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': cfg.csrfToken,
            },
            body: JSON.stringify({
                question_id: questionId,
                choice_id: choiceId,
            }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.expired) {
                    setSaveStatus('error', 'زمان تمام شد');
                    form.submit();
                    return;
                }
                if (!data.ok) {
                    setSaveStatus('error', data.error || 'خطا در ذخیره');
                    return;
                }
                setSaveStatus('saved', 'ذخیره شد ✓');
                saveToStorage('q' + questionId, choiceId);
                updateProgress();
            })
            .catch(function () {
                setSaveStatus('error', 'آفلاین — پاسخ محلی ذخیره شد');
                saveToStorage('q' + questionId, choiceId);
            });
    }

    function restoreAnswers() {
        var server = cfg.savedAnswers || {};
        var local = {};
        try {
            local = JSON.parse(localStorage.getItem(storageKey) || '{}');
        } catch (e) { /* ignore */ }

        var merged = Object.assign({}, server, local);
        Object.keys(merged).forEach(function (qKey) {
            var choiceId = merged[qKey];
            var fieldName = qKey.indexOf('q') === 0 ? qKey : 'q' + qKey;
            var input = form.querySelector('input[name="' + fieldName + '"][value="' + choiceId + '"]');
            if (input) input.checked = true;
        });
        updateProgress();
    }

    function startTimer() {
        if (!hasLimit || timeLeft <= 0) {
            if (timerEl) timerEl.textContent = 'نامحدود';
            return;
        }
        function tick() {
            var m = Math.floor(timeLeft / 60);
            var s = timeLeft % 60;
            if (timerEl) timerEl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
            if (timerWrap) {
                timerWrap.classList.toggle('is-warning', timeLeft <= 60 && timeLeft > 0);
                timerWrap.classList.toggle('is-danger', timeLeft <= 15);
            }
            if (timeLeft <= 0) {
                setSaveStatus('error', 'زمان تمام شد — در حال ارسال…');
                form.submit();
                return;
            }
            timeLeft--;
            setTimeout(tick, 1000);
        }
        tick();
    }

    function scrollToQuestion(num) {
        var el = document.getElementById('q' + num);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.querySelectorAll('.qe-nav-btn').forEach(function (b) {
                b.classList.toggle('is-current', b.getAttribute('data-q-num') === String(num));
            });
        }
    }

    form.querySelectorAll('input[type="radio"]').forEach(function (input) {
        input.addEventListener('change', function () {
            var qId = input.name.replace('q', '');
            saveAnswer(qId, input.value);
        });
    });

    document.querySelectorAll('.qe-nav-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            scrollToQuestion(btn.getAttribute('data-q-num'));
        });
    });

    var reviewBtn = document.getElementById('btn-review-unanswered');
    if (reviewBtn) {
        reviewBtn.addEventListener('click', function () {
            var first = null;
            document.querySelectorAll('.qe-question').forEach(function (card, i) {
                var qid = card.getAttribute('data-question-id');
                if (!form.querySelector('input[name="q' + qid + '"]:checked') && !first) {
                    first = i + 1;
                }
            });
            if (first) scrollToQuestion(first);
            else alert('همه سوالات پاسخ داده شده‌اند 🎉');
        });
    }

    form.addEventListener('submit', function (e) {
        var unanswered = totalQuestions - form.querySelectorAll('input[type="radio"]:checked').length;
        if (unanswered > 0) {
            var ok = confirm(
                faNum(unanswered) + ' سوال بدون پاسخ مانده است.\nآیا مطمئنید می‌خواهید ثبت نهایی کنید؟'
            );
            if (!ok) {
                e.preventDefault();
            }
        }
    });

    window.addEventListener('beforeunload', function (e) {
        var unanswered = totalQuestions - form.querySelectorAll('input[type="radio"]:checked').length;
        if (unanswered > 0) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    restoreAnswers();
    startTimer();
    updateProgress();
})();
