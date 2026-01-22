const fileUploader = {
  init: function (settings) {
    const uploader = document.getElementById(settings.uploadContainer);

    if (!uploader) {
      console.error(
        `Uploader with ID "${settings.uploadContainer}" not found.`
      );
      return;
    }

    const inputElement = uploader.querySelector("input[type='file']");
    const previewContainer = uploader.querySelector(".preview");
    const errorMsg = uploader.querySelector(".error-msg");
    const uploadBtn = uploader.querySelector(".upload-btn");
    let uploadedFiles = [];

    // تنظیمات سفارشی
    const maxImages = settings.imageMaxFiles;
    const maxVideos = settings.videoMaxFiles;

    uploadBtn.addEventListener("click", () => {
      inputElement.click();
    });

    inputElement.addEventListener("change", (event) => {
      const file = event.target.files[0];

      if (file) {
        const isImage = file.type.startsWith("image/");
        const isVideo = file.type.startsWith("video/");
        const maxSize = isImage
          ? settings.imageFileSize * 1024 * 1024
          : settings.videoFileSize * 1024 * 1024;

        const imageFilesCount = uploadedFiles.filter((f) =>
          f.type.startsWith("image/")
        ).length;
        const videoFilesCount = uploadedFiles.filter((f) =>
          f.type.startsWith("video/")
        ).length;

        if (isImage && imageFilesCount >= maxImages) {
          errorMsg.textContent = `حداکثر تعداد عکس‌های قابل آپلود ${maxImages} فایل است.`;
          return;
        }
        if (isVideo && videoFilesCount >= maxVideos) {
          errorMsg.textContent = `حداکثر تعداد ویدیو‌های قابل آپلود ${maxVideos} فایل است.`;
          return;
        }

        if (file.size > maxSize) {
          errorMsg.textContent = "حجم فایل بیش از حد مجاز است!";
          event.target.value = ""; // پاک کردن فایل انتخاب شده
          return;
        }

        errorMsg.textContent = "";

        uploadedFiles.push(file);

        const fileItem = document.createElement("div");
        fileItem.classList.add("file-item");

        const deleteBtn = document.createElement("button");
        deleteBtn.classList.add("delete-btn");
        deleteBtn.innerHTML = "<i class='fi fi-rs-trash'></i>";
        deleteBtn.addEventListener("click", () => {
          uploadedFiles = uploadedFiles.filter((f) => f !== file);
          previewContainer.removeChild(fileItem);
        });

        if (isImage) {
          const img = document.createElement("img");
          img.src = URL.createObjectURL(file);
          fileItem.appendChild(img);
        } else if (isVideo) {
          const video = document.createElement("video");
          video.src = URL.createObjectURL(file);
          video.preload = "metadata";

          video.addEventListener("loadeddata", () => {
            video.currentTime = 5;
          });

          video.addEventListener("seeked", () => {
            const canvas = document.createElement("canvas");
            canvas.width = 120;
            canvas.height = 120;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const img = document.createElement("img");
            img.src = canvas.toDataURL();
            fileItem.appendChild(img);

            video.pause();
            video.src = "";
          });
        }

        const tag = document.createElement("div");
        tag.classList.add("file-tag");
        tag.textContent = isImage ? "عکس" : "ویدیو";
        fileItem.appendChild(tag);

        const progressBar = document.createElement("div");
        progressBar.classList.add("progress-bar");
        const progressFill = document.createElement("div");
        progressFill.classList.add("progress-fill");
        progressBar.appendChild(progressFill);
        fileItem.appendChild(progressBar);

        let uploadProgress = 0;
        const fakeUpload = setInterval(() => {
          uploadProgress += 10;
          progressFill.style.width = `${uploadProgress}%`;
          if (uploadProgress >= 100) {
            clearInterval(fakeUpload);
            progressBar.style.display = "none";
          }
        }, 200);

        fileItem.appendChild(deleteBtn);
        previewContainer.appendChild(fileItem);
      }
    });
  },
};
