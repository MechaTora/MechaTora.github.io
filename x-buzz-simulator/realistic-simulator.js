// Realistic X Buzz Simulator - Slow and Immersive
class RealisticXBuzzSimulator {
    constructor() {
        this.isSimulating = false;
        this.buzzData = {
            likes: 0,
            retweets: 0,
            replies: 0,
            views: 0
        };
        
        // Much slower and more realistic settings
        this.buzzSpeed = 2000; // 2 seconds between updates (much slower)
        this.maxBuzzDuration = 120000; // 2 minutes total duration
        this.currentPhase = 0;
        this.startTime = null;
        this.lastNotificationTime = 0;
        this.tweetTimestamp = null;
        
        this.initializeEventListeners();
        this.generateNotificationSound();
    }

    initializeEventListeners() {
        const tweetInput = document.getElementById('tweetInput');
        const tweetBtn = document.getElementById('tweetBtn');
        const charCount = document.getElementById('charCount');
        const imageBtn = document.getElementById('imageBtn');
        const imageInput = document.getElementById('imageInput');
        const removeImage = document.getElementById('removeImage');

        // Text input handling
        tweetInput.addEventListener('input', (e) => {
            const length = e.target.value.length;
            charCount.textContent = length;
            tweetBtn.disabled = length === 0;
            
            // Character count styling
            if (length > 260) {
                charCount.style.color = '#f91880';
            } else if (length > 240) {
                charCount.style.color = '#ffd400';
            } else {
                charCount.style.color = '#71767b';
            }
        });

        // Image handling
        imageBtn.addEventListener('click', () => imageInput.click());
        imageInput.addEventListener('change', this.handleImageUpload.bind(this));
        removeImage?.addEventListener('click', this.removeImage.bind(this));

        // Tweet button
        tweetBtn.addEventListener('click', this.startRealisticBuzz.bind(this));

        // Keyboard shortcuts
        tweetInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                if (!tweetBtn.disabled) {
                    this.startRealisticBuzz();
                }
            }
        });
    }

    async startRealisticBuzz() {
        if (this.isSimulating) return;

        const tweetText = document.getElementById('tweetInput').value.trim();
        if (!tweetText) return;

        this.isSimulating = true;
        this.resetBuzzData();
        this.startTime = Date.now();
        this.tweetTimestamp = this.getRelativeTime(0);

        // Show the tweet
        this.displayTweet(tweetText);
        
        // Start the slow, realistic buzz simulation
        await this.simulateRealisticSpread();
        
        this.isSimulating = false;
        this.resetComposer();
    }

    displayTweet(text) {
        const viralTweet = document.getElementById('viralTweet');
        const viralTweetText = document.getElementById('viralTweetText');
        const viralTweetImage = document.getElementById('viralTweetImage');
        const viralImage = document.getElementById('viralImage');
        const timestampEl = document.getElementById('tweetTimestamp');

        viralTweetText.textContent = text;
        timestampEl.textContent = '今';
        
        // Show image if uploaded
        const previewImage = document.getElementById('previewImage');
        if (previewImage?.src && previewImage.src !== window.location.href) {
            viralImage.src = previewImage.src;
            viralTweetImage.style.display = 'block';
        } else {
            viralTweetImage.style.display = 'none';
        }

        viralTweet.style.display = 'block';
        viralTweet.scrollIntoView({ behavior: 'smooth' });

        // Update trending if hashtags exist
        const hashtags = text.match(/#\w+/g);
        if (hashtags && hashtags.length > 0) {
            setTimeout(() => this.updateTrending(hashtags[0]), 30000); // Show trending after 30 seconds
        }
    }

    async simulateRealisticSpread() {
        // Realistic phases with much slower progression
        const phases = [
            { 
                duration: 20000, // 20 seconds - early discovery
                likeMultiplier: 1,
                retweetMultiplier: 0.2,
                replyMultiplier: 0.1,
                viewMultiplier: 10,
                description: "数人が反応し始める"
            },
            { 
                duration: 30000, // 30 seconds - gaining traction
                likeMultiplier: 3,
                retweetMultiplier: 0.6,
                replyMultiplier: 0.3,
                viewMultiplier: 25,
                description: "フォロワーに拡散"
            },
            { 
                duration: 40000, // 40 seconds - viral growth
                likeMultiplier: 8,
                retweetMultiplier: 1.5,
                replyMultiplier: 0.8,
                viewMultiplier: 50,
                description: "バイラル開始"
            },
            { 
                duration: 30000, // 30 seconds - peak viral
                likeMultiplier: 15,
                retweetMultiplier: 3,
                replyMultiplier: 1.5,
                viewMultiplier: 100,
                description: "バイラルピーク"
            }
        ];

        let totalElapsed = 0;

        for (let i = 0; i < phases.length; i++) {
            const phase = phases[i];
            const phaseStart = Date.now();
            this.currentPhase = i;

            // Show subtle phase notification
            if (i > 1) { // Only show for viral phases
                this.showPhaseNotification(phase.description);
            }

            while (Date.now() - phaseStart < phase.duration) {
                // Generate realistic numbers
                this.generateRealisticNumbers(phase);
                
                // Update display
                this.updateDisplay();
                
                // Update timestamp
                this.updateTimestamp();
                
                // Occasional notifications (much less frequent)
                if (Date.now() - this.lastNotificationTime > 10000 && Math.random() < 0.3) {
                    this.addFloatingNotification();
                    this.lastNotificationTime = Date.now();
                }

                // Show viral overlay only at peak
                if (i === 3 && Date.now() - phaseStart > 15000 && Date.now() - phaseStart < 18000) {
                    this.showViralOverlay();
                }

                await this.sleep(this.buzzSpeed);
            }
            
            totalElapsed += phase.duration;
        }
    }

    generateRealisticNumbers(phase) {
        // Much more conservative number generation
        const baseIncrement = Math.random() * 3 + 1; // 1-4 base increment
        const timeBonus = Math.min(this.currentPhase, 3); // Progressive bonus
        
        // Likes (most common interaction)
        const likeIncrease = Math.floor(baseIncrement * phase.likeMultiplier * (0.8 + Math.random() * 0.4));
        this.buzzData.likes += likeIncrease;
        
        // Retweets (much fewer than likes)
        if (Math.random() < 0.7) {
            const retweetIncrease = Math.floor(baseIncrement * phase.retweetMultiplier * (0.5 + Math.random() * 0.5));
            this.buzzData.retweets += retweetIncrease;
        }
        
        // Replies (even fewer)
        if (Math.random() < 0.5) {
            const replyIncrease = Math.floor(baseIncrement * phase.replyMultiplier * (0.3 + Math.random() * 0.7));
            this.buzzData.replies += replyIncrease;
        }
        
        // Views (grow much faster)
        const viewIncrease = Math.floor(baseIncrement * phase.viewMultiplier * (1 + Math.random()));
        this.buzzData.views += viewIncrease;
    }

    updateDisplay() {
        // Update counters with smooth animations
        this.updateCounter('likeCount', this.buzzData.likes);
        this.updateCounter('retweetCount', this.buzzData.retweets);
        this.updateCounter('replyCount', this.buzzData.replies);
        this.updateCounter('viewCount', this.buzzData.views);
        
        // Subtle sound effect occasionally
        if (Math.random() < 0.1) {
            this.playSubtleNotificationSound();
        }
    }

    updateCounter(elementId, value) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        if (value !== currentValue) {
            // Animate number change
            element.classList.add('number-pop');
            element.textContent = this.formatNumber(value);
            
            setTimeout(() => {
                element.classList.remove('number-pop');
            }, 400);
        }
    }

    updateTimestamp() {
        const elapsed = Date.now() - this.startTime;
        const timestampEl = document.getElementById('tweetTimestamp');
        timestampEl.textContent = this.getRelativeTime(elapsed);
    }

    getRelativeTime(elapsed) {
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        
        if (seconds < 10) return '今';
        if (seconds < 60) return `${seconds}秒`;
        if (minutes < 60) return `${minutes}分`;
        
        const hours = Math.floor(minutes / 60);
        return `${hours}時間`;
    }

    addFloatingNotification() {
        const notificationTypes = [
            {
                type: 'like',
                messages: [
                    "👍 田中太郎さんがいいねしました",
                    "❤️ 佐藤花子さんがいいねしました",
                    "👍 山田次郎さんがいいねしました",
                    "❤️ 鈴木美咲さんがいいねしました"
                ]
            },
            {
                type: 'repost',
                messages: [
                    "🔄 きのこたけのこさんがリポストしました",
                    "🔄 テック愛好家さんがリポストしました",
                    "🔄 カフェ好きさんがリポストしました"
                ]
            },
            {
                type: 'reply',
                messages: [
                    "💬 田中太郎さんが返信しました: 「同感です！」",
                    "💬 佐藤花子さんが返信しました: 「面白いですね」",
                    "💬 山田次郎さんが返信しました: 「なるほど！」",
                    "💬 きのこたけのこさんが返信しました: 「これは話題になりそう」"
                ]
            },
            {
                type: 'quote',
                messages: [
                    "📝 テック愛好家さんが引用ポストしました: 「これは興味深い話題ですね」",
                    "📝 カフェ好きさんが引用ポストしました: 「みんなはどう思う？」",
                    "📝 ニュース速報さんが引用ポストしました: 「話題の投稿をチェック」"
                ]
            },
            {
                type: 'follow',
                messages: [
                    "👤 新しいフォロワーが3人増えました",
                    "👤 あなたをフォローする人が増えています",
                    "👤 フォロワーが急増中です"
                ]
            },
            {
                type: 'trending',
                messages: [
                    "🔥 あなたの投稿がトレンドに入りました",
                    "📈 エンゲージメントが急上昇中",
                    "🌟 注目の投稿になりました",
                    "📊 多くの人に拡散されています"
                ]
            }
        ];

        // Choose notification type based on current phase
        let selectedType;
        const rand = Math.random();
        
        if (this.currentPhase === 0) {
            // Early phase: mostly likes and few replies
            selectedType = rand < 0.7 ? notificationTypes[0] : notificationTypes[2];
        } else if (this.currentPhase === 1) {
            // Growing phase: likes, reposts, replies
            if (rand < 0.4) selectedType = notificationTypes[0];
            else if (rand < 0.7) selectedType = notificationTypes[1];
            else selectedType = notificationTypes[2];
        } else if (this.currentPhase === 2) {
            // Viral phase: all types including quotes
            if (rand < 0.3) selectedType = notificationTypes[0];
            else if (rand < 0.5) selectedType = notificationTypes[1];
            else if (rand < 0.7) selectedType = notificationTypes[2];
            else if (rand < 0.85) selectedType = notificationTypes[3];
            else selectedType = notificationTypes[4];
        } else {
            // Peak viral: quotes, trending, followers
            if (rand < 0.2) selectedType = notificationTypes[1];
            else if (rand < 0.4) selectedType = notificationTypes[3];
            else if (rand < 0.7) selectedType = notificationTypes[4];
            else selectedType = notificationTypes[5];
        }

        const message = selectedType.messages[Math.floor(Math.random() * selectedType.messages.length)];
        
        const notificationEl = document.createElement('div');
        notificationEl.className = `floating-notification ${selectedType.type}-notification`;
        notificationEl.innerHTML = `
            <div class="notification-content">
                <span class="notification-text">${message}</span>
                <span class="notification-time">今</span>
            </div>
        `;
        
        const container = document.getElementById('notificationContainer');
        container.appendChild(notificationEl);
        
        // Add specific interaction effects
        this.addInteractionEffect(selectedType.type);
        
        // Remove after 6 seconds (longer to read)
        setTimeout(() => {
            notificationEl.style.animation = 'float-notification 0.5s ease-out reverse';
            setTimeout(() => {
                notificationEl.remove();
            }, 500);
        }, 6000);
    }

    addInteractionEffect(type) {
        const viralTweet = document.getElementById('viralTweet');
        
        switch(type) {
            case 'like':
                // Flash the like button
                const likeBtn = document.querySelector('#viralTweet .like-btn');
                likeBtn?.classList.add('interaction-flash');
                setTimeout(() => likeBtn?.classList.remove('interaction-flash'), 500);
                break;
                
            case 'repost':
                // Flash the repost button
                const retweetBtn = document.querySelector('#viralTweet .retweet-btn');
                retweetBtn?.classList.add('interaction-flash');
                setTimeout(() => retweetBtn?.classList.remove('interaction-flash'), 500);
                break;
                
            case 'reply':
                // Flash the reply button
                const replyBtn = document.querySelector('#viralTweet .reply-btn');
                replyBtn?.classList.add('interaction-flash');
                setTimeout(() => replyBtn?.classList.remove('interaction-flash'), 500);
                break;
                
            case 'quote':
                // Add quote effect to the whole tweet
                viralTweet?.classList.add('quoted-flash');
                setTimeout(() => viralTweet?.classList.remove('quoted-flash'), 1000);
                break;
                
            case 'follow':
                // No specific button flash for follows
                break;
                
            case 'trending':
                // Add trending effect to the whole tweet
                viralTweet?.classList.add('trending-flash');
                setTimeout(() => viralTweet?.classList.remove('trending-flash'), 1000);
                break;
        }
    }

    showPhaseNotification(description) {
        // Very subtle phase notification
        const notification = document.createElement('div');
        notification.className = 'floating-notification';
        notification.textContent = `📊 ${description}`;
        notification.style.background = 'rgba(29, 155, 240, 0.9)';
        
        const container = document.getElementById('notificationContainer');
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showViralOverlay() {
        const overlay = document.getElementById('viralOverlay');
        overlay.style.display = 'block';
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 3000);
        
        this.playViralSound();
    }

    updateTrending(hashtag) {
        const trendElement = document.getElementById('viralTrend');
        const trendTopic = document.getElementById('userTrend');
        
        if (trendElement && trendTopic) {
            trendTopic.textContent = hashtag;
            trendElement.style.display = 'block';
        }
    }

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            if (file.size > 5 * 1024 * 1024) {
                alert('画像サイズは5MB以下にしてください');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const previewImage = document.getElementById('previewImage');
                previewImage.src = e.target.result;
                document.getElementById('imagePreview').style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    removeImage() {
        document.getElementById('imagePreview').style.display = 'none';
        document.getElementById('imageInput').value = '';
    }

    resetComposer() {
        document.getElementById('tweetInput').value = '';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('tweetBtn').disabled = true;
        this.removeImage();
        
        // Reset character count styling
        document.getElementById('charCount').style.color = '#71767b';
    }

    resetBuzzData() {
        this.buzzData = {
            likes: 0,
            retweets: 0, 
            replies: 0,
            views: 0
        };
        this.currentPhase = 0;
        this.lastNotificationTime = 0;
        
        // Clear notifications
        document.getElementById('notificationContainer').innerHTML = '';
        
        // Hide trending
        const trendElement = document.getElementById('viralTrend');
        if (trendElement) {
            trendElement.style.display = 'none';
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    playSubtleNotificationSound() {
        if (!this.audioContext) return;

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // Very subtle, low volume sound
            oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.02, this.audioContext.currentTime + 0.01); // Very quiet
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.2);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + 0.2);
        } catch (error) {
            console.log('Audio not available');
        }
    }

    playViralSound() {
        if (!this.audioContext) return;

        try {
            // Slightly more prominent viral sound
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.05, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + 0.4);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + 0.4);
        } catch (error) {
            console.log('Audio not available');
        }
    }

    generateNotificationSound() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.log('Audio context not available');
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the realistic simulator
document.addEventListener('DOMContentLoaded', () => {
    new RealisticXBuzzSimulator();
    
    // Initialize AdSense
    if (typeof adsbygoogle !== 'undefined') {
        (adsbygoogle = window.adsbygoogle || []).push({});
    }
    
    console.log('🐦 Realistic X Buzz Simulator initialized');
});