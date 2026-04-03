import { useEffect, useState } from "react";
import "./EnvironmentBadge.css";

function EnvironmentBadge() {
  const [backendEnv, setBackendEnv] = useState("loading");
  const [frontendEnv, setFrontendEnv] = useState("unknown");

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // 프론트엔드 환경 판단
  const getFrontendEnvironment = () => {
    const hostname = window.location.hostname;
    const port = window.location.port;

    if (hostname === "localhost") {
      if (port === "80" || port === "" || port === "3000") {
        // Docker nginx는 80번 포트 사용
        return port === "5173" ? "local" : "local-docker";
      }
      return "local";
    }
    // localhost가 아닌 경우 서버 환경
    return "server";
  };

  useEffect(() => {
    // 프론트엔드 환경 설정
    setFrontendEnv(getFrontendEnvironment());

    // 백엔드 환경 조회
    const fetchBackendEnv = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        const data = await res.json();
        setBackendEnv(data.environment || "unknown");
      } catch (err) {
        setBackendEnv("offline");
      }
    };

    fetchBackendEnv();

    // 30초마다 갱신
    const interval = setInterval(fetchBackendEnv, 30000);
    return () => clearInterval(interval);
  }, [API_URL]);

  const getEnvColor = (env) => {
    switch (env) {
      case "local":
        return "#4CAF50"; // 녹색
      case "local-docker":
        return "#2196F3"; // 파란색
      case "server":
        return "#FF9800"; // 주황색
      case "offline":
        return "#f44336"; // 빨간색
      default:
        return "#9E9E9E"; // 회색
    }
  };

  const getEnvLabel = (env) => {
    switch (env) {
      case "local":
        return "로컬";
      case "local-docker":
        return "로컬도커";
      case "server":
        return "서버";
      case "offline":
        return "오프라인";
      default:
        return "알 수 없음";
    }
  };

  return (
    <div className="environment-badge">
      <div className="env-item">
        <span className="env-label">프론트:</span>
        <span
          className="env-value"
          style={{ backgroundColor: getEnvColor(frontendEnv) }}
        >
          {getEnvLabel(frontendEnv)}
        </span>
      </div>
      <div className="env-divider">|</div>
      <div className="env-item">
        <span className="env-label">백엔드:</span>
        <span
          className="env-value"
          style={{ backgroundColor: getEnvColor(backendEnv) }}
        >
          {getEnvLabel(backendEnv)}
        </span>
      </div>
    </div>
  );
}

export default EnvironmentBadge;
