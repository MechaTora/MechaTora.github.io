// 🐱 Cute Cat Site JavaScript

class CatSite {
    constructor() {
        this.currentCat = null;
        this.favorites = JSON.parse(localStorage.getItem('catFavorites')) || [];
        this.viewCount = parseInt(localStorage.getItem('catViewCount')) || 0;
        this.currentCategory = 'all';
        
        // Cat names list
        this.catNames = [
            'Whiskers', 'Luna', 'Max', 'Bella', 'Charlie', 'Lucy', 'Oliver', 'Lily',
            'Leo', 'Mia', 'Felix', 'Chloe', 'Tiger', 'Sophie', 'Smokey', 'Zoe'
        ];
        
        // Cat mood emotes
        this.catMoods = ['😊', '😻', '😸', '😺', '🥰', '😽', '😼', '🙀', '😿', '😾'];
        
        // Cat fun facts database
        this.catFacts = [
            "🐾 Cats sleep 12-16 hours a day. They're truly sleep professionals!",
            "😺 A cat's sense of smell is about 40 times better than humans.",
            "🎵 Cat purring at 25-50Hz is said to help improve human bone density.",
            "👃 Cat nose prints are unique like human fingerprints.",
            "🦷 Adult cats have 30 teeth.",
            "👀 Cats can see colors, but not as many as humans can.",
            "🐾 Cat paw pads are the only place cats sweat from and get moist when nervous.",
            "🌙 Cats are nocturnal animals and can see 6 times better than humans in the dark.",
            "💨 Cats can run up to 30 mph (48 km/h).",
            "🔄 Cats can rotate their bodies 180 degrees.",
            "📡 Cat whiskers work as ultra-high-performance sensors.",
            "🎯 Cats can make about 100 different vocal sounds.",
            "🧠 Cat brains are 90% similar to human brains in structure.",
            "⚡ Cat reflexes are about 7 times faster than humans.",
            "🌡️ Normal cat body temperature is 100.5-102.5°F (38-39°C), higher than humans."
        ];
        
        // Cat wisdom database by category
        this.catWisdom = {
            general: [
                { title: "Ancient Egypt Connection", text: "Cats were considered sacred in ancient Egypt and killing one was punishable by death!" },
                { title: "Feline Family Size", text: "A group of cats is called a 'clowder' and a group of kittens is called a 'kindle'." },
                { title: "Cat Communication", text: "Cats meow almost exclusively to communicate with humans, not other cats." },
                { title: "Landing Skills", text: "Cats always land on their feet due to their 'righting reflex' developed by 6-7 weeks old." },
                { title: "Memory Masters", text: "Cats have better short-term memory than dogs and can remember things for up to 16 hours." }
            ],
            health: [
                { title: "Healing Purrs", text: "Cat purring frequencies (20-50Hz) can promote bone healing and reduce pain in humans." },
                { title: "Stress Relief", text: "Petting a cat for just 10 minutes can significantly reduce stress hormones." },
                { title: "Heart Health", text: "Cat owners have a 40% lower risk of heart attack compared to non-pet owners." },
                { title: "Blood Pressure", text: "The sound of a cat purring can help lower blood pressure and promote relaxation." },
                { title: "Mental Health", text: "Cats provide emotional support and can help reduce symptoms of depression and anxiety." }
            ],
            behavior: [
                { title: "Kneading Behavior", text: "Cats knead with their paws because it reminds them of nursing as kittens." },
                { title: "Head Butting", text: "When cats head-butt you, they're marking you with their scent as part of their family." },
                { title: "Slow Blinks", text: "When cats slowly blink at you, it's their way of saying 'I love you' - try blinking back!" },
                { title: "Tail Signals", text: "A cat's tail position reveals their mood: up means happy, puffed means scared." },
                { title: "Hunting Instinct", text: "Even well-fed cats hunt because it's instinctual behavior, not hunger-driven." }
            ],
            history: [
                { title: "Ship Companions", text: "Cats were essential on ships to control rats, spreading them worldwide through maritime trade." },
                { title: "First Cat Show", text: "The world's first cat show was held in London in 1871 with 170 cats competing." },
                { title: "Famous Cats", text: "Ernest Hemingway's cats were polydactyl (6-toed), and their descendants still live at his museum." },
                { title: "Space Cats", text: "In 1963, France sent a cat named Félicette to space, making her the first and only cat astronaut." },
                { title: "Internet Fame", text: "The first cat video was recorded in 1894 by Thomas Edison, starting our obsession early!" }
            ]
        };
        
        // Wisdom widget state
        this.currentWisdomCategory = 'general';
        this.factsLearned = parseInt(localStorage.getItem('factsLearned')) || 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadNewCat();
        this.updateStats();
        this.displayFavorites();
        this.addHeartAnimation();
        this.initWisdomWidget();
    }
    
    setupEventListeners() {
        // Wait for DOM to be ready
        const newCatBtn = document.getElementById('newCatBtn');
        const saveCatBtn = document.getElementById('saveCat');
        const shareCatBtn = document.getElementById('shareCatBtn');
        const catImage = document.getElementById('catImage');
        
        if (newCatBtn) {
            newCatBtn.addEventListener('click', () => {
                console.log('New cat button clicked');
                this.loadNewCat();
            });
        }
        
        if (saveCatBtn) {
            saveCatBtn.addEventListener('click', () => {
                this.saveFavorite();
            });
        }
        
        if (shareCatBtn) {
            shareCatBtn.addEventListener('click', () => {
                this.shareCat();
            });
        }
        
        // Category buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectCategory(e.target.dataset.category);
                this.updateCategoryButtons(e.target);
            });
        });
        
        // Cat image click for purr effect
        if (catImage) {
            catImage.addEventListener('click', () => {
                this.addPurrEffect();
            });
        }
        
        // Wisdom widget event listeners
        const newWisdomBtn = document.getElementById('newWisdomBtn');
        const shareWisdomBtn = document.getElementById('shareWisdomBtn');
        
        if (newWisdomBtn) {
            newWisdomBtn.addEventListener('click', () => {
                this.loadNewWisdom();
            });
        }
        
        if (shareWisdomBtn) {
            shareWisdomBtn.addEventListener('click', () => {
                this.shareWisdom();
            });
        }
        
        // Wisdom category buttons
        document.querySelectorAll('.wisdom-cat-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectWisdomCategory(e.target.dataset.wisdomCategory);
                this.updateWisdomCategoryButtons(e.target);
            });
        });
    }
    
    async loadNewCat() {
        console.log('🐱 Loading new cat from APIs...');
        const loading = document.getElementById('loading');
        const catImage = document.getElementById('catImage');
        const catName = document.getElementById('catName');
        const catMood = document.getElementById('catMood');
        
        if (!loading || !catImage || !catName || !catMood) {
            console.error('❌ Required DOM elements not found');
            return;
        }
        
        // Show loading
        loading.style.display = 'flex';
        catImage.style.display = 'none';
        
        try {
            // Fetch cat from APIs
            const catData = await this.fetchRandomCat();
            console.log('📸 Cat data received:', catData);
            
            if (catData) {
                // Set random name and mood
                const randomName = this.catNames[Math.floor(Math.random() * this.catNames.length)];
                const randomMood = this.catMoods[Math.floor(Math.random() * this.catMoods.length)];
                
                this.currentCat = {
                    ...catData,
                    name: randomName,
                    mood: randomMood
                };
                
                // Update UI elements
                catName.textContent = randomName;
                catMood.textContent = randomMood;
                
                // Load the image
                catImage.onload = () => {
                    console.log('✅ Cat image displayed successfully');
                    loading.style.display = 'none';
                    catImage.style.display = 'block';
                    
                    // Show success notification
                    this.showNotification(`🐱 New ${catData.source} cat loaded!`, 'success');
                };
                
                catImage.onerror = () => {
                    console.error('❌ Cat image failed to display');
                    this.handleLoadError();
                };
                
                // Set the image source
                catImage.src = catData.url;
                catImage.alt = `Cute ${catData.breed || ''} cat from ${catData.source}`;
                
                // Safety timeout
                setTimeout(() => {
                    if (loading.style.display !== 'none') {
                        console.log('⏰ Loading timeout, forcing display');
                        loading.style.display = 'none';
                        catImage.style.display = 'block';
                    }
                }, 15000); // 15 second timeout
                
            } else {
                throw new Error('No cat data received');
            }
            
        } catch (error) {
            console.error('💥 Failed to load cat:', error);
            this.handleLoadError();
        }
        
        // Display random fun fact
        const randomFact = this.catFacts[Math.floor(Math.random() * this.catFacts.length)];
        const catFactElement = document.getElementById('catFact');
        if (catFactElement) {
            catFactElement.textContent = randomFact;
        }
        
        this.updateViewCount();
        this.createFloatingHearts();
    }
    
    async fetchRandomCat() {
        console.log('🐱 Starting to fetch cat from APIs...');
        
        const apis = [
            // The Cat API - Real cat photos (most reliable)
            {
                name: 'The Cat API',
                url: 'https://api.thecatapi.com/v1/images/search',
                parser: (data) => ({ 
                    url: data[0].url, 
                    id: data[0].id, 
                    source: 'thecatapi',
                    breed: data[0].breeds?.[0]?.name || 'Mixed'
                })
            },
            // CATAAS - Cat as a Service
            {
                name: 'CATAAS',
                url: null,
                parser: () => {
                    const timestamp = Date.now();
                    return { 
                        url: `https://cataas.com/cat?${timestamp}`, 
                        id: `cataas-${timestamp}`, 
                        source: 'cataas',
                        breed: 'Random'
                    };
                }
            },
            // HTTP Cats - Fun status code cats
            {
                name: 'HTTP Cats',
                url: null,
                parser: () => {
                    const codes = [200, 201, 202, 204, 206, 301, 302, 304, 400, 401, 403, 404, 405, 406, 409, 410, 418, 429, 500, 502, 503, 504];
                    const randomCode = codes[Math.floor(Math.random() * codes.length)];
                    return { 
                        url: `https://http.cat/${randomCode}`, 
                        id: `http-cat-${randomCode}`, 
                        source: 'httpcat',
                        breed: `HTTP ${randomCode}`
                    };
                }
            }
        ];
        
        // Try each API with proper error handling
        for (let i = 0; i < apis.length; i++) {
            const api = apis[i];
            
            try {
                console.log(`🔄 Trying ${api.name}...`);
                
                if (api.url) {
                    // API with JSON response
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
                    
                    const response = await fetch(api.url, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'User-Agent': 'Cat-Healing-Station/1.0'
                        },
                        mode: 'cors',
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    const result = api.parser(data);
                    console.log(`✅ ${api.name} successful:`, result);
                    return result;
                    
                } else {
                    // Direct image URL
                    const result = api.parser();
                    console.log(`✅ ${api.name} (direct) successful:`, result);
                    
                    // Test if the image actually loads
                    await this.testImageLoad(result.url);
                    return result;
                }
                
            } catch (error) {
                console.error(`❌ ${api.name} failed:`, error.message);
                
                // Continue to next API
                if (i < apis.length - 1) {
                    console.log(`🔄 Trying next API...`);
                    continue;
                }
            }
        }
        
        // All APIs failed - return emergency fallback
        console.log('🚨 All APIs failed, using emergency fallback');
        return {
            url: `data:image/svg+xml;base64,${btoa(`
                <svg xmlns="http://www.w3.org/2000/svg" width="500" height="400">
                    <rect width="500" height="400" fill="#FFB6C1"/>
                    <text x="250" y="180" font-size="80" text-anchor="middle">🐱</text>
                    <text x="250" y="240" font-size="24" text-anchor="middle" fill="#333">Emergency Cat</text>
                    <text x="250" y="270" font-size="16" text-anchor="middle" fill="#666">API temporarily unavailable</text>
                </svg>
            `)}`,
            id: `emergency-${Date.now()}`,
            source: 'emergency',
            breed: 'Emergency'
        };
    }
    
    // Test if an image URL actually loads
    testImageLoad(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => reject(new Error('Image failed to load'));
            img.src = url;
            
            // Timeout after 5 seconds
            setTimeout(() => reject(new Error('Image load timeout')), 5000);
        });
    }
    
    handleLoadError() {
        const loading = document.getElementById('loading');
        const catImage = document.getElementById('catImage');
        const catName = document.getElementById('catName');
        const catMood = document.getElementById('catMood');
        
        // Use the emergency SVG fallback that's already in fetchRandomCat
        const randomName = this.catNames[Math.floor(Math.random() * this.catNames.length)];
        const randomMood = this.catMoods[Math.floor(Math.random() * this.catMoods.length)];
        
        const emergencyFallback = `data:image/svg+xml;base64,${btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="500" height="400">
                <rect width="500" height="400" fill="#FFB6C1"/>
                <text x="250" y="180" font-size="80" text-anchor="middle">🐱</text>
                <text x="250" y="240" font-size="24" text-anchor="middle" fill="#333">Emergency Cat</text>
                <text x="250" y="270" font-size="16" text-anchor="middle" fill="#666">API temporarily unavailable</text>
            </svg>
        `)}`;
        
        catImage.src = emergencyFallback;
        catName.textContent = randomName;
        catMood.textContent = randomMood;
        
        catImage.onload = () => {
            loading.style.display = 'none';
            catImage.style.display = 'block';
        };
        
        this.currentCat = {
            url: emergencyFallback,
            id: `emergency-${Date.now()}`,
            source: 'emergency',
            name: randomName,
            mood: randomMood
        };
        
        document.getElementById('catFact').textContent = '🐱 Network seems slow, but here\'s still a cute cat for you!';
    }
    
    saveFavorite() {
        if (!this.currentCat) return;
        
        // Check for duplicates
        const exists = this.favorites.some(fav => fav.id === this.currentCat.id);
        if (exists) {
            this.showNotification(`${this.currentCat.name} is already in your favorites!`, 'info');
            return;
        }
        
        this.favorites.push({
            ...this.currentCat,
            savedAt: new Date().toISOString()
        });
        
        localStorage.setItem('catFavorites', JSON.stringify(this.favorites));
        this.displayFavorites();
        this.updateStats();
        this.showNotification(`${this.currentCat.name} saved to favorites! 💕`, 'success');
        this.createFloatingHearts();
        
        // Button animation
        const button = document.getElementById('saveCat');
        button.style.transform = 'scale(1.3) rotate(360deg)';
        setTimeout(() => {
            button.style.transform = '';
        }, 300);
    }
    
    removeFavorite(id) {
        this.favorites = this.favorites.filter(fav => fav.id !== id);
        localStorage.setItem('catFavorites', JSON.stringify(this.favorites));
        this.displayFavorites();
        this.updateStats();
        this.showNotification('Removed from favorites', 'info');
    }
    
    displayFavorites() {
        const grid = document.getElementById('favoritesGrid');
        
        if (this.favorites.length === 0) {
            grid.innerHTML = '<p class="no-favorites">No favorites yet. Save some cute cats!</p>';
            return;
        }
        
        grid.innerHTML = this.favorites.map(cat => `
            <div class="favorite-item">
                <img src="${cat.url}" alt="Favorite cat" loading="lazy">
                <button class="favorite-remove" onclick="catSite.removeFavorite('${cat.id}')">×</button>
            </div>
        `).join('');
    }
    
    selectCategory(category) {
        this.currentCategory = category;
        // Load new cat for selected category
        this.loadNewCat();
    }
    
    updateCategoryButtons(activeBtn) {
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
    
    updateViewCount() {
        this.viewCount++;
        localStorage.setItem('catViewCount', this.viewCount.toString());
        this.updateStats();
    }
    
    updateStats() {
        document.getElementById('viewCount').textContent = this.viewCount;
        document.getElementById('favoriteCount').textContent = this.favorites.length;
        
        // Calculate healing level dynamically
        const healingLevel = Math.min(100, Math.floor(this.viewCount * 5 + this.favorites.length * 10));
        document.getElementById('healingLevel').textContent = healingLevel;
    }
    
    addPurrEffect() {
        const catImage = document.getElementById('catImage');
        catImage.classList.add('purring');
        
        // Remove effect after 0.5 seconds
        setTimeout(() => {
            catImage.classList.remove('purring');
        }, 500);
        
        // Get cat name for message
        if (this.currentCat) {
            this.showNotification(`${this.currentCat.name} is purring 😻`, 'info');
        }
        
        this.createFloatingHearts();
    }
    
    createFloatingHearts() {
        const hearts = ['💕', '❤️', '💖', '💝', '🐾'];
        
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                const heart = document.createElement('div');
                heart.className = 'floating-heart';
                heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
                
                // Place at random position
                heart.style.left = Math.random() * window.innerWidth + 'px';
                heart.style.top = window.innerHeight - 100 + 'px';
                
                document.body.appendChild(heart);
                
                // Remove after 2 seconds
                setTimeout(() => {
                    if (heart.parentNode) {
                        heart.parentNode.removeChild(heart);
                    }
                }, 2000);
            }, i * 200);
        }
    }
    
    addHeartAnimation() {
        // Show hearts periodically on page load
        setInterval(() => {
            if (Math.random() < 0.3) { // 30% chance
                this.createFloatingHearts();
            }
        }, 5000);
    }
    
    async shareCat() {
        if (!this.currentCat) return;
        
        const shareData = {
            title: '🐱 Found a cute cat!',
            text: `Check out ${this.currentCat.name}${this.currentCat.mood}! This adorable cat will surely heal your heart 💕`,
            url: window.location.href
        };
        
        try {
            if (navigator.share) {
                await navigator.share(shareData);
                this.showNotification('Thanks for sharing! 🐱', 'success');
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(`${shareData.title}\n${shareData.text}\n${shareData.url}`);
                this.showNotification('Cat info copied to clipboard!', 'success');
            }
        } catch (error) {
            console.error('Share failed:', error);
            this.showNotification('Share failed', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#00b894' : type === 'error' ? '#e17055' : '#74b9ff'};
            color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
            font-weight: 500;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // Wisdom Widget Methods
    initWisdomWidget() {
        this.updateFactsLearned();
        this.loadNewWisdom();
    }
    
    loadNewWisdom() {
        const wisdomData = this.catWisdom[this.currentWisdomCategory];
        const randomWisdom = wisdomData[Math.floor(Math.random() * wisdomData.length)];
        
        const wisdomTitle = document.getElementById('wisdomTitle');
        const wisdomText = document.getElementById('wisdomText');
        const wisdomIcon = document.querySelector('.wisdom-icon');
        
        if (wisdomTitle && wisdomText) {
            wisdomTitle.textContent = randomWisdom.title;
            wisdomText.textContent = randomWisdom.text;
            
            // Update facts learned count
            this.factsLearned++;
            localStorage.setItem('factsLearned', this.factsLearned.toString());
            this.updateFactsLearned();
            
            // Add animation
            const wisdomCard = document.getElementById('wisdomCard');
            if (wisdomCard) {
                wisdomCard.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    wisdomCard.style.transform = 'scale(1)';
                }, 100);
            }
            
            // Random icon based on category
            const icons = {
                general: ['🐱', '😺', '😸', '😻'],
                health: ['💊', '❤️', '🩺', '💚'],
                behavior: ['🎯', '🧠', '👁️', '🐾'],
                history: ['📚', '🏛️', '🌍', '⏰']
            };
            
            const categoryIcons = icons[this.currentWisdomCategory] || icons.general;
            const randomIcon = categoryIcons[Math.floor(Math.random() * categoryIcons.length)];
            if (wisdomIcon) {
                wisdomIcon.textContent = randomIcon;
            }
            
            this.createFloatingHearts();
            this.showNotification(`New ${this.currentWisdomCategory} wisdom learned! 🧠`, 'success');
        }
    }
    
    selectWisdomCategory(category) {
        this.currentWisdomCategory = category;
        this.loadNewWisdom();
    }
    
    updateWisdomCategoryButtons(activeBtn) {
        document.querySelectorAll('.wisdom-cat-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
    
    updateFactsLearned() {
        const factsLearnedElement = document.getElementById('factsLearned');
        if (factsLearnedElement) {
            factsLearnedElement.textContent = this.factsLearned;
        }
    }
    
    async shareWisdom() {
        const wisdomTitle = document.getElementById('wisdomTitle');
        const wisdomText = document.getElementById('wisdomText');
        
        if (!wisdomTitle || !wisdomText) return;
        
        const shareData = {
            title: `🧠 Cat Wisdom: ${wisdomTitle.textContent}`,
            text: `${wisdomText.textContent}\n\nDiscover more at Cat Healing Station! 🐱`,
            url: window.location.href
        };
        
        try {
            if (navigator.share) {
                await navigator.share(shareData);
                this.showNotification('Wisdom shared successfully! 🧠', 'success');
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(`${shareData.title}\n${shareData.text}\n${shareData.url}`);
                this.showNotification('Wisdom copied to clipboard! 📋', 'success');
            }
        } catch (error) {
            console.error('Share failed:', error);
            this.showNotification('Share failed', 'error');
        }
    }
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize site
let catSite;
document.addEventListener('DOMContentLoaded', () => {
    console.log('🐱 DOM loaded, initializing Cat Healing Station...');
    try {
        catSite = new CatSite();
        console.log('✅ CatSite initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize CatSite:', error);
    }
});

// Periodic background color change for more dynamic feel - Lovely version
setInterval(() => {
    const colors = [
        'linear-gradient(135deg, #ff9ff3 0%, #f368e0 25%, #ff6b9d 50%, #ffa8cc 75%, #ffe0f0 100%)',
        'linear-gradient(135deg, #ffeaa7 0%, #fab1a0 25%, #fd79a8 50%, #ff6b9d 75%, #f368e0 100%)',
        'linear-gradient(135deg, #74b9ff 0%, #64b5f6 25%, #90caf9 50%, #bbdefb 75%, #e3f2fd 100%)',
        'linear-gradient(135deg, #55efc4 0%, #4fc3f7 25%, #29b6f6 50%, #03a9f4 75%, #e1f5fe 100%)'
    ];
    
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    document.body.style.background = randomColor;
}, 30000); // Change every 30 seconds