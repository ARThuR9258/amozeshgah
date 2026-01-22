Dropzone.options.fileImagesUpload = {
  paramName: "file",
  maxFilesize: 1,
  maxFiles: 10,
  url: "/your-upload-url",
  parallelUploads: 1,
  clickable: true,
  addRemoveLinks: true,
  uploadMultiple: true,
  acceptedFiles: ".webp,.jpg,.png",
  dictFileTooBig:
    "فایل بیش از حد بزرگ است ({{filesize}} مگابایت). حداکثر حجم مجاز: {{maxFilesize}} مگابایت.",
  dictDefaultMessage: "فایل‌هارو بکشید و رها کنید",
  dictFallbackMessage:
    "مرورگر شما از بارگذاری فایل با کشیدن و رها کردن (Drag & Drop) پشتیبانی نمی‌کند.",
  dictInvalidFileType: "نوع فایل پشتیبانی نمی‌شود.",
  dictMaxFilesExceeded: "تعداد فایل‌ها از حد مجاز بیشتر است.",
  dictResponseError: "سرور با کد {{statusCode}} پاسخ داد.",
  dictCancelUpload: "لغو بارگذاری فایل",
  dictUploadCanceled: "بارگذاری فایل لغو شد.",
  dictRemoveFile: "X",
  dictMaxFilesExceeded: "شما نمی‌توانید فایل‌های بیشتری بارگذاری کنید.",
  dictCancelUploadConfirmation:
    "آیا مطمئن هستید که می‌خواهید این بارگذاری را لغو کنید؟",
};
