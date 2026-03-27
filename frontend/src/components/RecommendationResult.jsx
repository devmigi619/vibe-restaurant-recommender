function RecommendationResult({ result }) {
  return (
    <div className="result-section">
      <div className="result-output">
        <h2>추천 결과</h2>
        <p className="result-text">{result.output}</p>
      </div>

      {result.intermediate_steps?.length > 0 && (
        <details className="steps-detail">
          <summary>에이전트 추론 과정 보기</summary>
          <div className="steps-list">
            {result.intermediate_steps.map((step, i) => (
              <div key={i} className="step-item">
                <div className="step-tool">🔧 {step.tool}</div>
                <div className="step-output">{step.output}</div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

export default RecommendationResult;
