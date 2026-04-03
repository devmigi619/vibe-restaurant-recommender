import { useState } from "react";
import ImageUpload from "./components/ImageUpload";
import RecommendationResult from "./components/RecommendationResult";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
  
  const handleImageUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setPreview(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/recommend`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "서버 오류가 발생했습니다.");
      }

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🍊 제주 감성 맛집 추천</h1>
        <p>지금 이 순간의 감성을 담은 사진을 올려주세요</p>
      </header>

      <main className="app-main">
        <ImageUpload onUpload={handleImageUpload} preview={preview} loading={loading} />

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            <div className="spinner" />
            <p>이미지 감성 분석 중...</p>
          </div>
        )}

        {result && <RecommendationResult result={result} />}
      </main>
    </div>
  );
}

export default App;
