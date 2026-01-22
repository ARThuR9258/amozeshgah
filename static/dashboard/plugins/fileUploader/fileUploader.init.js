fileUploader.init({
  uploadContainer: "uploader_review",
  imageMaxFiles: 5,
  imageFileSize: 5, // 5MB
  uploadMultiple: true,
});

fileUploader.init({
  uploadContainer: "uploader_videos",
  videoMaxFiles: 1,
  videoFileSize: 100, // 100MB
  uploadMultiple: false,
});
