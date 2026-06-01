(function () {
    'use strict';

    var cfg = window.EXAM_CONFIG;
    if (!cfg) return;

    var form = document.getElementById('exam-form');
    if (!form) return;

    var timerEl = document.getElementById('time-remaining');
    var timerBox = document.getElementById('exam-timer');
    var progressBar = document.getElementById('exam-progress-bar');
    var progressText = document.getElementById('exam-progress-text');
    var saveStatus = document.getElementById('exam-save-status');
    var submitBtn = document.getElementById('exam-submit-btn');

    var timeLeft = parseInt(cfg.timeLeft, 10) || 0;
    var total = parseInt(cfg.totalQuestions, 10) || 0;
    var saved = cfg.savedAnswers || {};
    var submitting = false;

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : '';
    }

    function countAnswered() {
        return form.querySelectorAll('.exam-option-input:checked').length;
    }

    function updateProgress(answered) {
        var n = typeof answered === 'number' ? answered : countAnswered();
        var pct = total ? Math.round((n / total) * 100) : 0;
        if (progressBar) {
            progressBar.style.width = pct + '%';
            progressBar.setAttribute('aria-valuenow', String(pct));
        }
        if (progressText) progressText.textContent = n + ' از ' + total + ' سوال';
    }

    function restoreSaved() {
        try {
            Object.keys(saved).forEach(function (qid) {
                var val = saved[qid];
                var input = form.querySelector('input[name="q' + qid + '"][value="' + val + '"]');
                if (input) input.checked = true;
            });
        } catch (e) {
            // ignore restore errors
        }
        updateProgress();
    }

    function setSaveStatus(msg, state) {
        if (!saveStatus) return;
        saveStatus.textContent = msg || '';
        saveStatus.classList.remove('is-saving', 'is-saved', 'is-error');
        if (state) saveStatus.classList.add(state);
    }

    function saveAnswer(questionId, choiceNumber) {
        setSaveStatus('در حال ذخیره…', 'is-saving');
        fetch(cfg.saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': cfg.csrfToken || getCookie('csrftoken'),
            },
            body: JSON.stringify({
                question_id: questionId,
                choice_number: choiceNumber,
            }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data && data.expired) {
                    autoSubmit();
                    return;
                }
                if (data && data.ok) {
                    setSaveStatus('ذخیره شد ✓', 'is-saved');
                    updateProgress(typeof data.answered === 'number' ? data.answered : countAnswered());
                } else {
                    setSaveStatus((data && data.error) ? data.error : 'خطا در ذخیره', 'is-error');
                }
            })
            .catch(function () {
                setSaveStatus('خطا در ارتباط', 'is-error');
            });
    }

    function autoSubmit() {
        if (submitting) return;
        submitting = true;
        if (submitBtn) submitBtn.disabled = true;
        form.submit();
    }

    function formatTime(sec) {
        var m = Math.floor(sec / 60);
        var s = sec % 60;
        return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    }

    function tickTimer() {
        if (timeLeft <= 0) {
            if (timerEl) timerEl.textContent = '00:00';
            autoSubmit();
            return;
        }
        if (timerEl) timerEl.textContent = formatTime(timeLeft);
        if (timerBox && timeLeft <= 60) timerBox.classList.add('is-low');
        timeLeft -= 1;
        window.setTimeout(tickTimer, 1000);
    }

    Array.prototype.forEach.call(form.querySelectorAll('.exam-option-input'), function (input) {
        input.addEventListener('change', function () {
            updateProgress();
            saveAnswer(this.dataset.questionId, this.value);
        });
    });

    restoreSaved();
    tickTimer();
})();

