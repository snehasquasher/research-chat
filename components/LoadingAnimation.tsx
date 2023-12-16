// LoadingAnimation.tsx
const LoadingAnimation: React.FC = () => {
    return (
      <div className="flex justify-center items-center py-4">
        <div className="loading-animation space-x-1 text-4xl text-gray-800"> {/* Increased font size */}
          <span className="dot animate-blink">.</span>
          <span className="dot animate-blink" style={{ animationDelay: '0.2s' }}>.</span>
          <span className="dot animate-blink" style={{ animationDelay: '0.4s' }}>.</span>
        </div>
      </div>
    );
};

export default LoadingAnimation;
