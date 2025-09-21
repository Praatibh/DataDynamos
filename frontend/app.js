// Application data from provided JSON
const appData = {
  misinformation_crisis: {
    global_impact: "3.8 billion people exposed to misinformation daily",
    india_statistics: {
      fake_news_incidents: 456789,
      affected_users: "890 million",
      election_misinformation: 23456,
      health_misinformation: 78901,
      financial_fraud: 34567
    },
    spread_speed: {
      fake_news: "6x faster than true news",
      reach: "1500% more engagement",
      platforms: ["WhatsApp", "Facebook", "Twitter", "YouTube", "Instagram"]
    }
  },
  ai_detection_stats: {
    accuracy_rate: 96.8,
    detection_speed: "0.8 seconds",
    content_types: ["Text", "Images", "Videos", "Audio", "Deepfakes"],
    languages_supported: ["Hindi", "English", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati"],
    daily_verifications: 125000,
    prevented_spread: 2.3
  },
  real_time_detections: [
    {
      id: "rt1",
      type: "deepfake_video",
      content: "Political leader making false statement",
      authenticity_score: 0.12,
      risk_level: "critical",
      platform: "Twitter",
      location: "Delhi",
      timestamp: "2025-09-20T12:15:00Z",
      prevented_shares: 45000
    },
    {
      id: "rt2",
      type: "manipulated_image",
      content: "Fake disaster scene",
      authenticity_score: 0.23,
      risk_level: "high",
      platform: "WhatsApp",
      location: "Mumbai",
      timestamp: "2025-09-20T12:10:00Z",
      prevented_shares: 23000
    },
    {
      id: "rt3",
      type: "false_text",
      content: "Misleading health advice",
      authenticity_score: 0.15,
      risk_level: "critical",
      platform: "Facebook",
      location: "Bangalore",
      timestamp: "2025-09-20T12:05:00Z",
      prevented_shares: 67000
    }
  ],
  trending_threats: [
    {
      category: "Election Manipulation",
      incidents: 3456,
      growth_rate: "+45%",
      severity: "critical",
      color: "#FF4444"
    },
    {
      category: "Health Misinformation",
      incidents: 2890,
      growth_rate: "+23%",
      severity: "high",
      color: "#FF6B35"
    },
    {
      category: "Financial Scams",
      incidents: 2234,
      growth_rate: "+67%",
      severity: "high",
      color: "#F7931E"
    },
    {
      category: "Deepfake Media",
      incidents: 1567,
      growth_rate: "+123%",
      severity: "critical",
      color: "#FF1744"
    }
  ],
  ai_technology: {
    models: [
      {
        name: "Gemini 2.0 Flash",
        capability: "Multimodal Analysis",
        accuracy: 96.8,
        speed: "0.8s",
        description: "Advanced language understanding and content analysis"
      },
      {
        name: "Vision AI Pro",
        capability: "Image Manipulation Detection",
        accuracy: 94.2,
        speed: "1.2s",
        description: "Deepfake and photo manipulation detection"
      },
      {
        name: "Audio Forensics AI",
        capability: "Voice Deepfake Detection",
        accuracy: 92.5,
        speed: "2.1s",
        description: "AI-generated voice and audio manipulation detection"
      }
    ]
  },
  success_metrics: {
    misinformation_stopped: 2340000,
    users_protected: 15600000,
    accuracy_improvement: "+23.5%",
    response_time_reduction: "-67%",
    community_contributions: 456000,
    lives_saved: 12000
  },
  community_network: {
    active_defenders: 156000,
    verified_contributors: 23400,
    fact_checkers: 890,
    government_partners: 45,
    media_partnerships: 234,
    educational_institutions: 567
  }
};

// Global variables
let charts = {};
let animationFrames = {};
let counters = {};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing TruthGuard AI Platform...');
  
  // Initialize all components
  initializeNavigation();
  initializeAnimatedCounters();
  initializeDetectionInterface();
  initializeCharts();
  initialize3DEffects();
  initializeRealTimeUpdates();
  initializeModalSystem();
  populateDynamicContent();
  
  console.log('TruthGuard AI Platform initialized successfully!');
});

// Navigation functionality with smooth scrolling - FIXED
function initializeNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section');
  
  // Handle navigation clicks - FIXED
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (!targetId || targetId === '#') return;
      
      const sectionId = targetId.substring(1);
      const targetSection = document.getElementById(sectionId);
      
      console.log('Navigating to:', sectionId, 'Found element:', !!targetSection);
      
      if (targetSection) {
        // Update active nav link
        navLinks.forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        
        // Smooth scroll to section
        targetSection.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        
        console.log('Navigation successful to:', sectionId);
      } else {
        console.error('Target section not found:', sectionId);
      }
    });
  });
  
  // Handle scroll spy - FIXED
  let scrollTimeout;
  window.addEventListener('scroll', function() {
    // Debounce scroll events
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      const scrollPos = window.scrollY + 150; // Offset for fixed nav
      
      sections.forEach(section => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        const id = section.getAttribute('id');
        
        if (scrollPos >= top && scrollPos < top + height) {
          navLinks.forEach(nav => nav.classList.remove('active'));
          const activeNav = document.querySelector(`[href="#${id}"]`);
          if (activeNav) {
            activeNav.classList.add('active');
          }
        }
      });
    }, 50);
  });
  
  console.log('Navigation initialized with', navLinks.length, 'links and', sections.length, 'sections');
}

// Animated counter functionality
function initializeAnimatedCounters() {
  const countersData = [
    { target: 3800000000, element: document.querySelector('[data-target="3800000000"]') },
    { target: 890000000, element: document.querySelector('[data-target="890000000"]') },
    { target: 6, element: document.querySelector('[data-target="6"]') },
    { target: 2340000, element: document.querySelector('[data-target="2340000"]') },
    { target: 125000, element: document.querySelector('[data-target="125000"]') },
    { target: 156000, element: document.querySelector('[data-target="156000"]') },
    { target: 23400, element: document.querySelector('[data-target="23400"]') },
    { target: 45, element: document.querySelector('[data-target="45"]') },
    { target: 567, element: document.querySelector('[data-target="567"]') }
  ];
  
  function animateCounter(counter, duration = 2000) {
    if (!counter.element) return;
    
    const start = 0;
    const target = counter.target;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(start + (target - start) * easeOut);
      
      // Format number with appropriate suffixes
      counter.element.textContent = formatNumber(current);
      
      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        counter.element.textContent = formatNumber(target);
      }
    }
    
    requestAnimationFrame(updateCounter);
  }
  
  function formatNumber(num) {
    if (num >= 1000000000) {
      return (num / 1000000000).toFixed(1) + 'B';
    } else if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(0) + 'K';
    }
    return num.toString();
  }
  
  // Intersection Observer to trigger animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = entry.target.getAttribute('data-target');
        const counter = countersData.find(c => c.target == target);
        if (counter && !counter.animated) {
          animateCounter(counter);
          counter.animated = true;
        }
      }
    });
  }, { threshold: 0.5 });
  
  countersData.forEach(counter => {
    if (counter.element) {
      observer.observe(counter.element);
    }
  });
  
  console.log('Animated counters initialized');
}

// Detection interface functionality - COMPLETELY FIXED
function initializeDetectionInterface() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');
  const analyzeTextButton = document.getElementById('analyzeText');
  const textInput = document.getElementById('textInput');
  const startDetectionButton = document.getElementById('startDetection');
  
  console.log('Detection interface elements found:', {
    tabButtons: tabButtons.length,
    tabContents: tabContents.length,
    analyzeTextButton: !!analyzeTextButton,
    textInput: !!textInput,
    startDetectionButton: !!startDetectionButton
  });
  
  // Tab switching functionality - FIXED
  tabButtons.forEach((button, index) => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const tabId = this.getAttribute('data-tab');
      console.log('Tab clicked:', tabId, 'Button index:', index);
      
      // Remove active class from all tabs and contents
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabContents.forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
      });
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Show corresponding content
      const targetContent = document.getElementById(`${tabId}-content`);
      console.log('Target content element:', tabId + '-content', 'Found:', !!targetContent);
      
      if (targetContent) {
        targetContent.classList.add('active');
        targetContent.style.display = 'block';
        console.log('Tab switched successfully to:', tabId);
      } else {
        console.error('Target content not found for tab:', tabId);
      }
    });
  });
  
  // Text analysis functionality - FIXED
  if (analyzeTextButton && textInput) {
    // Ensure text input is properly styled and visible
    textInput.style.color = 'white';
    textInput.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
    textInput.style.border = '1px solid rgba(255, 255, 255, 0.2)';
    
    // Test input functionality
    textInput.addEventListener('input', function() {
      console.log('Text input value changed:', this.value);
    });
    
    analyzeTextButton.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const text = textInput.value.trim();
      console.log('Analyze button clicked, text length:', text.length);
      
      if (!text) {
        alert('Please enter some text to analyze.');
        return;
      }
      
      console.log('Starting AI analysis for text:', text.substring(0, 100) + '...');
      startAIAnalysis(text, 'text');
    });
    
    console.log('Text analysis functionality initialized');
  } else {
    console.error('Text analysis elements not found:', {
      analyzeTextButton: !!analyzeTextButton,
      textInput: !!textInput
    });
  }
  
  // File upload functionality - FIXED
  const uploadZones = document.querySelectorAll('.upload-zone');
  console.log('Upload zones found:', uploadZones.length);
  
  uploadZones.forEach((zone, index) => {
    const input = zone.querySelector('input[type="file"]');
    if (!input) {
      console.error('File input not found in upload zone', index);
      return;
    }
    
    zone.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Upload zone clicked:', index);
      input.click();
    });
    
    zone.addEventListener('dragover', function(e) {
      e.preventDefault();
      this.style.borderColor = '#3B82F6';
      this.style.background = 'rgba(59, 130, 246, 0.1)';
    });
    
    zone.addEventListener('dragleave', function(e) {
      e.preventDefault();
      this.style.borderColor = '';
      this.style.background = '';
    });
    
    zone.addEventListener('drop', function(e) {
      e.preventDefault();
      this.style.borderColor = '';
      this.style.background = '';
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        console.log('File dropped:', files[0].name);
        handleFileUpload(files[0]);
      }
    });
    
    input.addEventListener('change', function() {
      if (this.files.length > 0) {
        console.log('File selected:', this.files[0].name);
        handleFileUpload(this.files[0]);
      }
    });
  });
  
  // Start detection from hero button - FIXED
  if (startDetectionButton) {
    startDetectionButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Start detection button clicked');
      
      const detectionSection = document.getElementById('detection');
      if (detectionSection) {
        detectionSection.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        console.log('Scrolled to detection section');
      }
    });
  }
  
  console.log('Detection interface initialized successfully');
}

// File upload handler
function handleFileUpload(file) {
  const fileType = file.type.split('/')[0];
  const fileName = file.name;
  
  console.log(`Analyzing ${fileType}: ${fileName}`);
  startAIAnalysis(fileName, fileType);
}

// AI Analysis simulation with realistic steps - FIXED
function startAIAnalysis(content, type) {
  console.log('Starting AI analysis for:', content, 'Type:', type);
  showModal('loadingModal');
  
  const loadingSteps = [
    'Initializing multimodal detection...',
    'Analyzing content patterns...',
    'Cross-referencing with known databases...',
    'Applying Gemini 2.0 Flash analysis...',
    'Performing blockchain verification...',
    'Calculating authenticity score...',
    'Generating comprehensive report...'
  ];
  
  let stepIndex = 0;
  const progressElement = document.getElementById('loadingProgress');
  
  const stepInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length) {
      if (progressElement) {
        progressElement.textContent = loadingSteps[stepIndex];
      }
      console.log('Analysis step:', loadingSteps[stepIndex]);
      stepIndex++;
    } else {
      clearInterval(stepInterval);
      hideModal('loadingModal');
      
      // Generate realistic results
      const results = generateAnalysisResults(content, type);
      displayResults(results);
      console.log('Analysis complete, showing results');
    }
  }, 800);
}

// Generate realistic analysis results
function generateAnalysisResults(content, type) {
  // Simulate different authenticity scores based on content patterns
  let authenticityScore;
  let verdict;
  let confidence;
  let riskFactors = [];
  
  // Simple content analysis simulation
  const suspiciousWords = ['breaking', 'urgent', 'shocking', 'viral', 'fake', 'hoax'];
  const contentLower = content.toLowerCase();
  const suspiciousCount = suspiciousWords.filter(word => contentLower.includes(word)).length;
  
  if (suspiciousCount >= 2) {
    authenticityScore = Math.random() * 0.3; // Low authenticity
    riskFactors.push('Sensational language detected');
    riskFactors.push('Pattern matches known misinformation');
  } else if (suspiciousCount === 1) {
    authenticityScore = 0.3 + Math.random() * 0.4; // Medium authenticity
    riskFactors.push('Some concerning elements found');
  } else {
    authenticityScore = 0.7 + Math.random() * 0.3; // High authenticity
  }
  
  // Determine verdict based on score
  if (authenticityScore < 0.3) {
    verdict = 'Likely Misinformation';
    confidence = 85 + Math.random() * 10;
  } else if (authenticityScore < 0.7) {
    verdict = 'Requires Review';
    confidence = 70 + Math.random() * 15;
  } else {
    verdict = 'Likely Authentic';
    confidence = 80 + Math.random() * 15;
  }
  
  return {
    content,
    type,
    authenticityScore,
    verdict,
    confidence: Math.round(confidence),
    riskFactors,
    timestamp: new Date().toISOString(),
    blockchainHash: generateBlockchainHash(),
    processingTime: (0.5 + Math.random() * 1).toFixed(1) + 's'
  };
}

// Generate mock blockchain hash
function generateBlockchainHash() {
  return '0x' + Array.from({length: 16}, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');
}

// Display analysis results - FIXED
function displayResults(results) {
  const resultsPanel = document.getElementById('resultsPanel');
  const resultsContent = document.getElementById('resultsContent');
  
  if (!resultsPanel || !resultsContent) {
    console.error('Results panel not found');
    showModal('resultsModal');
    
    // Display in modal instead
    const modalResults = document.getElementById('modalResults');
    if (modalResults) {
      displayResultsInModal(results, modalResults);
    }
    return;
  }
  
  const scoreColor = results.authenticityScore < 0.3 ? '#FF4444' : 
                    results.authenticityScore < 0.7 ? '#F7931E' : '#00FF88';
  
  const scorePercentage = Math.round(results.authenticityScore * 100);
  
  resultsContent.innerHTML = `
    <div class="glass-container" style="margin-bottom: 2rem;">
      <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: ${scoreColor}; font-size: 2rem; margin-bottom: 0.5rem;">
          ${results.verdict}
        </h3>
        <p style="opacity: 0.8;">Content Analysis Complete</p>
      </div>
      
      <div class="authenticity-meter" style="margin-bottom: 2rem;">
        <div class="meter-container" style="background: rgba(255, 255, 255, 0.1); height: 20px; border-radius: 10px; overflow: hidden; position: relative;">
          <div class="meter-fill" style="width: 0%; height: 100%; background: ${scoreColor}; border-radius: 10px; transition: width 2s ease;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem; opacity: 0.8;">
          <span>Misinformation</span>
          <span style="font-weight: 700; color: ${scoreColor};">${scorePercentage}%</span>
          <span>Authentic</span>
        </div>
      </div>
      
      <div class="results-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
        <div class="detail-item">
          <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Confidence Level</div>
          <div style="font-weight: 600; color: #00FF88;">${results.confidence}%</div>
        </div>
        <div class="detail-item">
          <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Processing Time</div>
          <div style="font-weight: 600;">${results.processingTime}</div>
        </div>
        <div class="detail-item">
          <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Content Type</div>
          <div style="font-weight: 600; text-transform: capitalize;">${results.type}</div>
        </div>
        <div class="detail-item">
          <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Blockchain Hash</div>
          <div style="font-family: monospace; font-size: 0.75rem; color: #3B82F6;">${results.blockchainHash}</div>
        </div>
      </div>
      
      ${results.riskFactors.length > 0 ? `
        <div class="risk-factors">
          <h4 style="margin-bottom: 1rem; color: #FF6B35;">Risk Factors Identified:</h4>
          <ul style="list-style: none; padding: 0;">
            ${results.riskFactors.map(factor => `
              <li style="background: rgba(255, 68, 68, 0.1); padding: 0.5rem 1rem; margin-bottom: 0.5rem; border-radius: 8px; border-left: 3px solid #FF4444;">
                ${factor}
              </li>
            `).join('')}
          </ul>
        </div>
      ` : ''}
      
      <div class="ai-explanation">
        <h4 style="margin-bottom: 1rem;">AI Analysis Explanation:</h4>
        <p style="line-height: 1.6; opacity: 0.9;">
          Our advanced AI system analyzed this content using multiple detection algorithms including 
          pattern recognition, source verification, and contextual analysis. The system cross-referenced 
          the content against our database of known misinformation patterns and verified sources.
        </p>
      </div>
    </div>
  `;
  
  resultsPanel.classList.add('show');
  resultsPanel.style.display = 'block';
  resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  
  // Animate the meter fill
  setTimeout(() => {
    const meterFill = resultsContent.querySelector('.meter-fill');
    if (meterFill) {
      meterFill.style.width = `${scorePercentage}%`;
    }
  }, 500);
  
  console.log('Results displayed successfully');
}

// Display results in modal fallback
function displayResultsInModal(results, modalResults) {
  const scoreColor = results.authenticityScore < 0.3 ? '#FF4444' : 
                    results.authenticityScore < 0.7 ? '#F7931E' : '#00FF88';
  const scorePercentage = Math.round(results.authenticityScore * 100);
  
  modalResults.innerHTML = `
    <div style="text-align: center; margin-bottom: 2rem;">
      <h3 style="color: ${scoreColor}; font-size: 2rem; margin-bottom: 0.5rem;">
        ${results.verdict}
      </h3>
      <p style="opacity: 0.8;">Content Analysis Complete</p>
    </div>
    
    <div class="authenticity-meter" style="margin-bottom: 2rem;">
      <div class="meter-container" style="background: rgba(255, 255, 255, 0.1); height: 20px; border-radius: 10px; overflow: hidden; position: relative;">
        <div class="meter-fill" style="width: ${scorePercentage}%; height: 100%; background: ${scoreColor}; border-radius: 10px; transition: width 2s ease;"></div>
      </div>
      <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem; opacity: 0.8;">
        <span>Misinformation</span>
        <span style="font-weight: 700; color: ${scoreColor};">${scorePercentage}%</span>
        <span>Authentic</span>
      </div>
    </div>
    
    <div class="results-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
      <div class="detail-item">
        <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Confidence Level</div>
        <div style="font-weight: 600; color: #00FF88;">${results.confidence}%</div>
      </div>
      <div class="detail-item">
        <div style="font-size: 0.875rem; opacity: 0.7; margin-bottom: 0.25rem;">Processing Time</div>
        <div style="font-weight: 600;">${results.processingTime}</div>
      </div>
    </div>
  `;
}

// Initialize Charts
function initializeCharts() {
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded, retrying...');
    setTimeout(initializeCharts, 1000);
    return;
  }
  
  initializeCrisisChart();
  console.log('Charts initialized');
}

// Crisis chart showing misinformation spread
function initializeCrisisChart() {
  const ctx = document.getElementById('crisisChart');
  if (!ctx) return;
  
  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(255, 68, 68, 0.3)');
  gradient.addColorStop(1, 'rgba(255, 68, 68, 0.05)');
  
  charts.crisis = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
      datasets: [
        {
          label: 'Misinformation Incidents',
          data: [1200, 1800, 2400, 3100, 3800, 4200, 4800, 5200, 5600],
          borderColor: '#FF4444',
          backgroundColor: gradient,
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#FF4444',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 6
        },
        {
          label: 'Successfully Detected',
          data: [800, 1400, 2000, 2700, 3400, 3900, 4500, 4900, 5300],
          borderColor: '#00FF88',
          backgroundColor: 'rgba(0, 255, 136, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#00FF88',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: 'rgba(255, 255, 255, 0.8)',
            usePointStyle: true,
            padding: 20
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'white',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        },
        y: {
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        }
      }
    }
  });
}

// Initialize 3D effects and animations
function initialize3DEffects() {
  initializeNeuralNetwork();
  initializeNetworkVisualization();
  console.log('3D effects initialized');
}

// Neural network animation
function initializeNeuralNetwork() {
  const networkContainer = document.getElementById('neuralNetwork');
  if (!networkContainer) return;
  
  const neurons = networkContainer.querySelectorAll('.neuron');
  const connectionsContainer = document.getElementById('networkConnections');
  
  if (connectionsContainer) {
    // Create connection lines between neurons
    const inputNeurons = networkContainer.querySelectorAll('.input .neuron');
    const hiddenNeurons = networkContainer.querySelectorAll('.hidden .neuron');
    const outputNeurons = networkContainer.querySelectorAll('.output .neuron');
    
    function createConnection(from, to, delay = 0) {
      const line = document.createElement('div');
      line.style.position = 'absolute';
      line.style.height = '2px';
      line.style.background = 'linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent)';
      line.style.transformOrigin = 'left center';
      line.style.animation = `connectionPulse 2s infinite ${delay}s`;
      
      const fromRect = from.getBoundingClientRect();
      const toRect = to.getBoundingClientRect();
      const containerRect = networkContainer.getBoundingClientRect();
      
      const x1 = fromRect.left + fromRect.width/2 - containerRect.left;
      const y1 = fromRect.top + fromRect.height/2 - containerRect.top;
      const x2 = toRect.left + toRect.width/2 - containerRect.left;
      const y2 = toRect.top + toRect.height/2 - containerRect.top;
      
      const length = Math.sqrt((x2-x1)**2 + (y2-y1)**2);
      const angle = Math.atan2(y2-y1, x2-x1) * 180 / Math.PI;
      
      line.style.left = x1 + 'px';
      line.style.top = y1 + 'px';
      line.style.width = length + 'px';
      line.style.transform = `rotate(${angle}deg)`;
      
      connectionsContainer.appendChild(line);
    }
    
    // Connect input to hidden layer
    inputNeurons.forEach((input, i) => {
      hiddenNeurons.forEach((hidden, j) => {
        createConnection(input, hidden, (i + j) * 0.1);
      });
    });
    
    // Connect hidden to output layer
    hiddenNeurons.forEach((hidden, i) => {
      outputNeurons.forEach((output, j) => {
        createConnection(hidden, output, (i + j) * 0.1 + 0.5);
      });
    });
  }
  
  // Add connection pulse animation CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes connectionPulse {
      0%, 100% { opacity: 0.2; transform: scaleX(0.5); }
      50% { opacity: 1; transform: scaleX(1); }
    }
  `;
  document.head.appendChild(style);
}

// Community network visualization
function initializeNetworkVisualization() {
  const networkContainer = document.getElementById('networkContainer');
  if (!networkContainer) return;
  
  // Create network nodes
  const nodes = [];
  const nodeCount = 20;
  
  for (let i = 0; i < nodeCount; i++) {
    const node = document.createElement('div');
    node.style.position = 'absolute';
    node.style.width = Math.random() * 10 + 8 + 'px';
    node.style.height = node.style.width;
    node.style.borderRadius = '50%';
    node.style.background = i < 5 ? '#00FF88' : '#3B82F6';
    node.style.boxShadow = `0 0 ${Math.random() * 20 + 10}px currentColor`;
    node.style.left = Math.random() * 80 + 10 + '%';
    node.style.top = Math.random() * 80 + 10 + '%';
    node.style.animation = `networkFloat ${Math.random() * 10 + 15}s infinite linear`;
    
    networkContainer.appendChild(node);
    nodes.push(node);
  }
  
  // Add floating animation
  const networkStyle = document.createElement('style');
  networkStyle.textContent = `
    @keyframes networkFloat {
      0% { transform: translate(0, 0) scale(1); }
      25% { transform: translate(${Math.random() * 40 - 20}px, ${Math.random() * 40 - 20}px) scale(1.1); }
      50% { transform: translate(${Math.random() * 40 - 20}px, ${Math.random() * 40 - 20}px) scale(0.9); }
      75% { transform: translate(${Math.random() * 40 - 20}px, ${Math.random() * 40 - 20}px) scale(1.05); }
      100% { transform: translate(0, 0) scale(1); }
    }
  `;
  document.head.appendChild(networkStyle);
}

// Initialize real-time updates
function initializeRealTimeUpdates() {
  populateThreatsList();
  populateDetectionsFeed();
  
  // Update feeds every 10 seconds
  setInterval(() => {
    updateDetectionsFeed();
  }, 10000);
  
  console.log('Real-time updates initialized');
}

// Populate threats list
function populateThreatsList() {
  const threatsList = document.getElementById('threatsList');
  if (!threatsList) return;
  
  threatsList.innerHTML = appData.trending_threats.map(threat => `
    <div class="threat-item" style="border-left-color: ${threat.color};">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <h4 style="margin: 0; font-size: 1rem;">${threat.category}</h4>
        <span style="color: ${threat.color}; font-weight: 600;">${threat.growth_rate}</span>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="opacity: 0.8; font-size: 0.875rem;">${threat.incidents.toLocaleString()} incidents</span>
        <span style="background: ${threat.severity === 'critical' ? '#FF4444' : '#FF6B35'}; 
                     color: white; padding: 0.25rem 0.5rem; border-radius: 10px; font-size: 0.75rem;">
          ${threat.severity.toUpperCase()}
        </span>
      </div>
    </div>
  `).join('');
}

// Populate detections feed
function populateDetectionsFeed() {
  const detectionsFeed = document.getElementById('detectionsFeed');
  if (!detectionsFeed) return;
  
  const detections = appData.real_time_detections.map(detection => {
    const timeAgo = getTimeAgo(new Date(detection.timestamp));
    return `
      <div class="detection-item">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <strong>${detection.content}</strong>
          <span style="font-size: 0.75rem; opacity: 0.7;">${timeAgo}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="opacity: 0.8;">${detection.platform} • ${detection.location}</span>
          <span style="color: #00FF88; font-weight: 600;">${detection.prevented_shares.toLocaleString()} shares prevented</span>
        </div>
      </div>
    `;
  }).join('');
  
  detectionsFeed.innerHTML = detections;
}

// Update detections feed with new data
function updateDetectionsFeed() {
  const newDetection = generateRandomDetection();
  const detectionsFeed = document.getElementById('detectionsFeed');
  if (!detectionsFeed) return;
  
  const detectionElement = document.createElement('div');
  detectionElement.className = 'detection-item';
  detectionElement.style.opacity = '0';
  detectionElement.style.transform = 'translateY(-20px)';
  detectionElement.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
      <strong>${newDetection.content}</strong>
      <span style="font-size: 0.75rem; opacity: 0.7;">Just now</span>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <span style="opacity: 0.8;">${newDetection.platform} • ${newDetection.location}</span>
      <span style="color: #00FF88; font-weight: 600;">${newDetection.prevented_shares.toLocaleString()} shares prevented</span>
    </div>
  `;
  
  detectionsFeed.insertBefore(detectionElement, detectionsFeed.firstChild);
  
  // Animate in
  setTimeout(() => {
    detectionElement.style.transition = 'all 0.5s ease';
    detectionElement.style.opacity = '1';
    detectionElement.style.transform = 'translateY(0)';
  }, 100);
  
  // Remove oldest item if too many
  const items = detectionsFeed.querySelectorAll('.detection-item');
  if (items.length > 5) {
    items[items.length - 1].remove();
  }
}

// Generate random detection for demo
function generateRandomDetection() {
  const contents = [
    "Viral health claim spreading rapidly",
    "Suspicious political advertisement",
    "Doctored celebrity image detected",
    "False economic news identified",
    "Misleading weather information"
  ];
  
  const platforms = ["WhatsApp", "Facebook", "Twitter", "Instagram", "YouTube"];
  const locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune"];
  
  return {
    content: contents[Math.floor(Math.random() * contents.length)],
    platform: platforms[Math.floor(Math.random() * platforms.length)],
    location: locations[Math.floor(Math.random() * locations.length)],
    prevented_shares: Math.floor(Math.random() * 50000) + 10000
  };
}

// Get time ago string
function getTimeAgo(date) {
  const now = new Date();
  const diffInMinutes = Math.floor((now - date) / (1000 * 60));
  
  if (diffInMinutes < 1) return 'Just now';
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
  return `${Math.floor(diffInMinutes / 1440)}d ago`;
}

// Modal system - FIXED
function initializeModalSystem() {
  const modals = document.querySelectorAll('.modal');
  
  modals.forEach(modal => {
    const backdrop = modal.querySelector('.modal-backdrop');
    const closeButton = modal.querySelector('.modal-close');
    
    if (backdrop) {
      backdrop.addEventListener('click', () => {
        hideModal(modal.id);
      });
    }
    
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        hideModal(modal.id);
      });
    }
  });
  
  // Close modal on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const visibleModal = document.querySelector('.modal:not(.hidden)');
      if (visibleModal) {
        hideModal(visibleModal.id);
      }
    }
  });
  
  console.log('Modal system initialized');
}

// Show modal
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    console.log('Modal shown:', modalId);
  }
}

// Hide modal
function hideModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    console.log('Modal hidden:', modalId);
  }
}

// Populate dynamic content
function populateDynamicContent() {
  // Add tech card interactions
  const techCards = document.querySelectorAll('.tech-card');
  techCards.forEach((card, index) => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-10px) scale(1.05)';
      this.style.boxShadow = '0 25px 50px rgba(59, 130, 246, 0.4)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = '';
      this.style.boxShadow = '';
    });
  });
  
  // Add globe hotspot interactions
  const hotspots = document.querySelectorAll('.hotspot');
  hotspots.forEach(hotspot => {
    hotspot.addEventListener('mouseenter', function() {
      const location = this.getAttribute('data-location');
      this.style.transform = 'scale(2) translateZ(20px)';
      this.setAttribute('title', `Misinformation detected in ${location}`);
    });
    
    hotspot.addEventListener('mouseleave', function() {
      this.style.transform = '';
    });
  });
  
  console.log('Dynamic content populated');
}

// Utility functions
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Add scroll animations
function initializeScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);
  
  // Observe elements for animation
  const animateElements = document.querySelectorAll('.problem-card, .dashboard-card, .tech-card, .stat-card');
  animateElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
}

// Initialize scroll animations after DOM load
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(initializeScrollAnimations, 500);
});

// Performance monitoring
function initializePerformanceMonitoring() {
  if ('performance' in window) {
    window.addEventListener('load', () => {
      const timing = performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      console.log(`Page load time: ${loadTime}ms`);
    });
  }
}

initializePerformanceMonitoring();