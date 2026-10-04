const {
  useState,
  useEffect,
  useRef
} = React;
const App = () => {
  const containerRef = useRef(null);
  const chatRef = useRef(null);
  const panelsRef = useRef([]);
  const [messages, setMessages] = useState([{
    role: 'agent',
    text: 'SYSTEM ONLINE. AWAITING INPUT...'
  }]);
  const [inputValue, setInputValue] = useState('');
  useEffect(() => {
    // Check if GSAP is available in the environment
    if (typeof gsap !== 'undefined') {
      // Initialization Animation
      gsap.fromTo(containerRef.current, {
        opacity: 0,
        scale: 0.9,
        rotationX: 15
      }, {
        opacity: 1,
        scale: 1,
        rotationX: 0,
        duration: 1.5,
        ease: "power4.out"
      });
      gsap.fromTo(panelsRef.current, {
        y: 50,
        opacity: 0
      }, {
        y: 0,
        opacity: 1,
        duration: 1,
        stagger: 0.2,
        delay: 0.5,
        ease: "back.out(1.7)"
      });
      gsap.fromTo(chatRef.current, {
        x: -50,
        opacity: 0
      }, {
        x: 0,
        opacity: 1,
        duration: 1,
        delay: 1,
        ease: "power3.out"
      });
    }
  }, []);
  const handleSendMessage = e => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    setMessages([...messages, {
      role: 'user',
      text: inputValue
    }]);
    setInputValue('');

    // Mock Agent Response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'agent',
        text: 'PROCESSING DIRECTIVE: ENCRYPTED KERNEL SYNC.'
      }]);
      if (typeof gsap !== 'undefined' && chatRef.current) {
        const newMsg = chatRef.current.lastElementChild;
        gsap.fromTo(newMsg, {
          opacity: 0,
          x: -20
        }, {
          opacity: 1,
          x: 0,
          duration: 0.5
        });
      }
    }, 1000);
  };
  const dashboardStyles = {
    minHeight: '100vh',
    backgroundColor: '#000000',
    color: '#E0E0E0',
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
    display: 'flex',
    flexDirection: 'column',
    padding: '2rem',
    overflow: 'hidden',
    perspective: '1000px'
  };
  const headerStyles = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    paddingBottom: '1rem'
  };
  const glassmorphismStyle = {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(16px)',
    WebkitBackdropFilter: 'blur(16px)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.5)',
    borderRadius: '16px',
    padding: '1.5rem',
    transformStyle: 'preserve-3d'
  };
  const gridStyles = {
    display: 'grid',
    gridTemplateColumns: '1fr 3fr',
    gap: '2rem',
    flexGrow: 1
  };
  const metricsGridStyles = {
    display: 'grid',
    gridTemplateRows: 'repeat(3, 1fr)',
    gap: '1.5rem'
  };
  const chatContainerStyles = {
    ...glassmorphismStyle,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between'
  };
  const inputStyles = {
    width: '100%',
    background: 'rgba(0, 0, 0, 0.5)',
    border: '1px solid rgba(0, 255, 255, 0.2)',
    color: '#00FFFF',
    padding: '1rem',
    borderRadius: '8px',
    outline: 'none',
    boxShadow: 'inset 0 0 10px rgba(0,255,255,0.05)',
    transition: 'all 0.3s ease'
  };
  const metricPanelStyles = {
    ...glassmorphismStyle,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'flex-start',
    position: 'relative',
    overflow: 'hidden'
  };
  const addPanelRef = el => {
    if (el && !panelsRef.current.includes(el)) {
      panelsRef.current.push(el);
    }
  };
  return /*#__PURE__*/React.createElement("div", {
    style: dashboardStyles,
    ref: containerRef
  }, /*#__PURE__*/React.createElement("header", {
    style: headerStyles
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '12px',
      height: '12px',
      borderRadius: '50%',
      background: '#00FFFF',
      boxShadow: '0 0 10px #00FFFF, 0 0 20px #00FFFF'
    }
  }), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontSize: '1.5rem',
      letterSpacing: '4px',
      fontWeight: 300,
      color: '#FFFFFF'
    }
  }, "NEXUS ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: '#00FFFF',
      fontWeight: 600
    }
  }, "AGENT OS"))), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '0.8rem',
      letterSpacing: '2px',
      color: 'rgba(255,255,255,0.4)'
    }
  }, "SECURE KERNEL v9.4.2 // SAMSUNG ADVANCED LABS")), /*#__PURE__*/React.createElement("div", {
    style: gridStyles
  }, /*#__PURE__*/React.createElement("div", {
    style: metricsGridStyles
  }, [{
    title: 'CORE COMPUTE',
    value: '94.2%',
    color: '#00FFFF'
  }, {
    title: 'NEURAL LINK',
    value: 'ACTIVE',
    color: '#FF0055'
  }, {
    title: 'VRAM ALLOCATION',
    value: '14.8 GB',
    color: '#B000FF'
  }].map((metric, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: metricPanelStyles,
    ref: addPanelRef
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '4px',
      height: '100%',
      background: metric.color,
      boxShadow: `0 0 15px ${metric.color}`
    }
  }), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: '0 0 0.5rem 0',
      fontSize: '0.8rem',
      color: 'rgba(255,255,255,0.5)',
      letterSpacing: '2px'
    }
  }, metric.title), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '2rem',
      fontWeight: 200,
      color: '#FFF',
      textShadow: `0 0 20px ${metric.color}66`
    }
  }, metric.value)))), /*#__PURE__*/React.createElement("div", {
    style: chatContainerStyles
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flexGrow: 1,
      overflowY: 'auto',
      padding: '1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    },
    ref: chatRef
  }, messages.map((msg, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
      background: msg.role === 'user' ? 'rgba(0, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
      border: msg.role === 'user' ? '1px solid rgba(0, 255, 255, 0.2)' : '1px solid rgba(255, 255, 255, 0.1)',
      padding: '1rem 1.5rem',
      borderRadius: '12px',
      maxWidth: '80%',
      color: msg.role === 'user' ? '#00FFFF' : '#E0E0E0',
      fontFamily: msg.role === 'agent' ? "'JetBrains Mono', monospace" : "inherit",
      fontSize: '0.95rem',
      letterSpacing: msg.role === 'agent' ? '1px' : 'normal',
      boxShadow: msg.role === 'user' ? '0 4px 20px rgba(0, 255, 255, 0.1)' : 'none'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '0.6rem',
      color: 'rgba(255,255,255,0.3)',
      marginBottom: '0.4rem',
      textTransform: 'uppercase'
    }
  }, msg.role), msg.text))), /*#__PURE__*/React.createElement("form", {
    onSubmit: handleSendMessage,
    style: {
      marginTop: '1rem',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "text",
    value: inputValue,
    onChange: e => setInputValue(e.target.value),
    placeholder: "ENTER DIRECTIVE...",
    style: inputStyles
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      right: '1rem',
      top: '50%',
      transform: 'translateY(-50%)',
      width: '8px',
      height: '8px',
      background: '#00FFFF',
      borderRadius: '50%',
      boxShadow: '0 0 10px #00FFFF',
      animation: 'pulse 2s infinite'
    }
  })))), /*#__PURE__*/React.createElement("style", {
    dangerouslySetInnerHTML: {
      __html: `
        @keyframes pulse {
          0% { opacity: 0.5; box-shadow: 0 0 5px #00FFFF; }
          50% { opacity: 1; box-shadow: 0 0 15px #00FFFF; }
          100% { opacity: 0.5; box-shadow: 0 0 5px #00FFFF; }
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
      `
    }
  }));
};

// Render directly to root to simplify the build process without exports
const rootNode = document.getElementById('root');
const root = ReactDOM.createRoot(rootNode);
root.render(/*#__PURE__*/React.createElement(App, null));
