document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-analysis');
    const stepInput = document.getElementById('step-input');
    const stepScan = document.getElementById('step-scan');
    const stepResult = document.getElementById('step-result');
    const scanBar = document.getElementById('scan-bar');
    
    const resumeInput = document.getElementById('resume-input');
    const jdInput = document.getElementById('jd-input');
    const originalPreview = document.getElementById('original-preview');
    const optimizedPreview = document.getElementById('optimized-preview');

    startBtn.addEventListener('click', () => {
        if (!resumeInput.value || !jdInput.value) {
            alert('Please provide both your current resume and the target job description.');
            return;
        }

        // 1. Switch to Scan Mode
        stepInput.style.display = 'none';
        stepScan.style.display = 'flex';

        // 2. Animate Scan Bar
        let progress = 0;
        const interval = setInterval(() => {
            progress += 2;
            scanBar.style.width = progress + '%';
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(showResults, 500);
            }
        }, 50);
    });

    function showResults() {
        stepScan.style.display = 'none';
        stepResult.style.display = 'block';

        const originalText = resumeInput.value;
        const jdText = jdInput.value.toLowerCase();

        // Simulate AI Optimization
        // 1. Identify common tech keywords likely present in JD
        const keywords = [
            'react', 'javascript', 'python', 'node.js', 'sql', 'aws', 
            'agile', 'scrum', 'leadership', 'scalability', 'performance',
            'design patterns', 'typescript', 'docker', 'kubernetes', 'rest api'
        ];

        const foundKeywords = keywords.filter(kw => jdText.includes(kw));

        // 2. Prepare Previews
        originalPreview.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit;">${originalText}</pre>`;
        
        // 3. Create Optimized Version
        let optimizedText = originalText;
        
        // Inject found keywords if they aren't already prominent
        if (foundKeywords.length > 0) {
            const skillAddition = `\n\n[AI Optimized Additions]\nTechnical Proficiency: ${foundKeywords.join(', ')}`;
            optimizedText += skillAddition;
        }

        // Highlight keywords in the preview
        let displayHtml = optimizedText.replace(/\n/g, '<br>');
        foundKeywords.forEach(kw => {
            const regex = new RegExp(`(${kw})`, 'gi');
            displayHtml = displayHtml.replace(regex, '<span class="keyword-highlight">$1</span>');
        });

        optimizedPreview.innerHTML = `
            <div class="optimized-badge">ATS Score: 98%</div>
            <div style="font-family: inherit;">${displayHtml}</div>
        `;
    }
});
