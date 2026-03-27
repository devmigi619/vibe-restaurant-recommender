import { useRef } from "react";

function ImageUpload({ onUpload, preview, loading }) {
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div className="upload-section">
      <div
        className={`upload-zone ${loading ? "loading" : ""}`}
        onClick={() => !loading && inputRef.current.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        {preview ? (
          <img src={preview} alt="업로드된 이미지" className="preview-image" />
        ) : (
          <div className="upload-placeholder">
            <span className="upload-icon">📷</span>
            <p>사진을 드래그하거나 클릭해서 업로드</p>
            <p className="upload-hint">오늘의 날씨, 풍경, 분위기가 담긴 사진이면 뭐든 OK</p>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        style={{ display: "none" }}
        onChange={(e) => handleFile(e.target.files[0])}
      />

      {preview && !loading && (
        <button className="retry-btn" onClick={() => inputRef.current.click()}>
          다른 사진으로 다시 시도
        </button>
      )}
    </div>
  );
}

export default ImageUpload;
