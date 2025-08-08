// 会社行きたくないメーター - メインアプリケーション
class CompanyHateMeter {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.monthlyChart = null;
        this.markers = new Map();
        this.prefectureData = new Map(); // 都道府県別データ
        this.prefectureBoundaries = new Map(); // 都道府県境界線レイヤー
        
        // Firebase Database参照
        this.database = window.database;
        this.postsRef = this.database.ref('posts');
        this.statisticsRef = this.database.ref('statistics');
        this.prefecturesRef = this.database.ref('prefectures');
        
        this.init();
    }

    async init() {
        console.log('🚀 会社行きたくないメーター 初期化開始');
        
        // 地図初期化
        this.initMap();
        
        // 位置情報取得
        await this.getLocation();
        
        // イベントリスナー設定
        this.setupEventListeners();
        
        // 統計チャート初期化
        this.initChart();
        
        // ランキング初期化
        this.initRankings();
        
        // Firebaseからリアルタイムデータ読み込み
        this.setupRealtimeListeners();
        
        console.log('✅ アプリケーション初期化完了');
    }

    initMap() {
        // 日本中心の地図を初期化
        this.map = L.map('map').setView([36.2048, 138.2529], 6);
        
        // OpenStreetMapタイル追加
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        // 都道府県境界線を読み込み
        this.loadPrefectureBoundaries();
        
        console.log('🗾 地図初期化完了');
    }

    async getLocation() {
        const locationInfo = document.getElementById('locationInfo');
        
        if (!navigator.geolocation) {
            locationInfo.innerHTML = `
                <div class="error">
                    位置情報がサポートされていません
                </div>
            `;
            return;
        }

        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5分
                });
            });

            this.userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            // 逆ジオコーディング（簡易版）
            const locationName = await this.reverseGeocode(
                this.userLocation.lat, 
                this.userLocation.lng
            );

            locationInfo.innerHTML = `
                <div style="color: var(--primary-blue);">
                    📍 現在地: ${locationName}
                </div>
            `;

            // 地図の中心を現在地に移動
            this.map.setView([this.userLocation.lat, this.userLocation.lng], 10);

            console.log('📍 位置情報取得完了:', locationName);

        } catch (error) {
            console.warn('位置情報取得エラー:', error);
            locationInfo.innerHTML = `
                <div class="error">
                    位置情報の取得に失敗しました<br>
                    手動で地域を選択してください
                </div>
            `;
            this.showManualLocationSelect();
        }
    }

    async reverseGeocode(lat, lng) {
        try {
            // Nominatim API（OpenStreetMapの逆ジオコーディング）
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1&accept-language=ja`
            );
            const data = await response.json();
            
            const address = data.address;
            if (address) {
                const city = address.city || address.town || address.village || address.county;
                const prefecture = address.state;
                return `${prefecture} ${city}`;
            }
            return '位置情報';
        } catch (error) {
            console.warn('逆ジオコーディングエラー:', error);
            return '位置不明';
        }
    }

    setupEventListeners() {
        const hateButton = document.getElementById('hateButton');
        
        hateButton.addEventListener('click', () => {
            this.submitHate();
        });

        // 都道府県選択のイベントリスナー
        const prefectureSelect = document.getElementById('prefectureSelect');
        if (prefectureSelect) {
            prefectureSelect.addEventListener('change', (e) => {
                this.onPrefectureSelect(e.target.value);
            });
        }
    }

    showManualLocationSelect() {
        const manualSelect = document.getElementById('manualLocationSelect');
        if (manualSelect) {
            manualSelect.style.display = 'block';
        }
    }

    onPrefectureSelect(prefecture) {
        if (!prefecture) return;

        // 選択された都道府県を現在位置として設定
        this.userLocation = {
            prefecture: prefecture,
            manual: true
        };

        // 位置情報表示を更新
        const locationInfo = document.getElementById('locationInfo');
        locationInfo.innerHTML = `
            <div style="color: var(--cyber-blue);">
                📍 選択地域: ${prefecture}
            </div>
        `;

        // 地図を選択された都道府県の中心に移動
        const prefectureCenter = this.getPrefectureCenter(prefecture);
        if (prefectureCenter) {
            this.map.setView([prefectureCenter.lat, prefectureCenter.lng], 8);
        }

        console.log('🏠 手動選択完了:', prefecture);
    }

    getPrefectureCenter(prefecture) {
        // 主要都道府県の中心座標
        const prefectureCenters = {
            '北海道': {lat: 43.2203, lng: 142.8635},
            '青森県': {lat: 40.5858, lng: 140.6917},
            '岩手県': {lat: 39.7036, lng: 141.1527},
            '宮城県': {lat: 38.7222, lng: 140.8719},
            '秋田県': {lat: 39.7186, lng: 140.1024},
            '山形県': {lat: 38.6503, lng: 140.3331},
            '福島県': {lat: 37.7608, lng: 140.4747},
            '茨城県': {lat: 36.3418, lng: 140.4469},
            '栃木県': {lat: 36.5658, lng: 139.8836},
            '群馬県': {lat: 36.3911, lng: 139.0608},
            '埼玉県': {lat: 35.8617, lng: 139.6455},
            '千葉県': {lat: 35.6074, lng: 140.1065},
            '東京都': {lat: 35.6762, lng: 139.6503},
            '神奈川県': {lat: 35.4478, lng: 139.6425},
            '新潟県': {lat: 37.9026, lng: 139.0232},
            '富山県': {lat: 36.6953, lng: 137.2113},
            '石川県': {lat: 36.5944, lng: 136.6256},
            '福井県': {lat: 36.0652, lng: 136.2217},
            '山梨県': {lat: 35.6642, lng: 138.5686},
            '長野県': {lat: 36.6513, lng: 138.1814},
            '岐阜県': {lat: 35.3912, lng: 136.7223},
            '静岡県': {lat: 34.9769, lng: 138.3831},
            '愛知県': {lat: 35.1815, lng: 136.9066},
            '三重県': {lat: 34.7303, lng: 136.5086},
            '滋賀県': {lat: 35.0045, lng: 135.8686},
            '京都府': {lat: 35.0211, lng: 135.7556},
            '大阪府': {lat: 34.6937, lng: 135.5023},
            '兵庫県': {lat: 34.6913, lng: 135.1830},
            '奈良県': {lat: 34.6851, lng: 135.8048},
            '和歌山県': {lat: 34.2261, lng: 135.1675},
            '鳥取県': {lat: 35.5038, lng: 134.2380},
            '島根県': {lat: 35.4723, lng: 133.0505},
            '岡山県': {lat: 34.6617, lng: 133.9341},
            '広島県': {lat: 34.3965, lng: 132.4596},
            '山口県': {lat: 34.1861, lng: 131.4706},
            '徳島県': {lat: 34.0658, lng: 134.5592},
            '香川県': {lat: 34.3401, lng: 134.0434},
            '愛媛県': {lat: 33.8417, lng: 132.7658},
            '高知県': {lat: 33.5597, lng: 133.5311},
            '福岡県': {lat: 33.6064, lng: 130.4181},
            '佐賀県': {lat: 33.2494, lng: 130.2989},
            '長崎県': {lat: 32.7503, lng: 129.8779},
            '熊本県': {lat: 32.7898, lng: 130.7417},
            '大分県': {lat: 33.2382, lng: 131.6126},
            '宮崎県': {lat: 31.9077, lng: 131.4202},
            '鹿児島県': {lat: 31.5602, lng: 130.5581},
            '沖縄県': {lat: 26.2124, lng: 127.6792}
        };

        return prefectureCenters[prefecture] || null;
    }

    async loadPrefectureBoundaries() {
        try {
            // 日本の都道府県境界データを取得
            console.log('🗾 都道府県境界線読み込み中...');
            
            // 無料のGeoJSONデータソースを使用
            const response = await fetch('https://raw.githubusercontent.com/dataofjapan/land/master/japan.geojson');
            const geoJsonData = await response.json();

            // 境界線スタイル（より明確に）
            const boundaryStyle = {
                color: '#ffffff', // 白い境界線でくっきりと
                weight: 3,
                opacity: 0.9,
                fillColor: 'rgba(0, 245, 255, 0.2)',
                fillOpacity: 0.3,
                dashArray: '2, 4', // 点線で視認性向上
                lineCap: 'round',
                lineJoin: 'round'
            };

            // GeoJSONレイヤーを地図に追加
            const boundaryLayer = L.geoJSON(geoJsonData, {
                style: boundaryStyle,
                onEachFeature: (feature, layer) => {
                    // 都道府県名の表示
                    if (feature.properties && feature.properties.nam_ja) {
                        const prefName = feature.properties.nam_ja;
                        
                        // ホバー時の強調表示
                        layer.on('mouseover', () => {
                            layer.setStyle({
                                weight: 5,
                                color: '#ff006e', // サイバーピンク
                                fillOpacity: 0.6,
                                dashArray: null // 実線に変更
                            });
                        });

                        layer.on('mouseout', () => {
                            // 元のスタイルに戻す（投稿数に応じた色を維持）
                            this.updateSinglePrefectureColor(prefName, layer);
                        });

                        // クリック時の情報表示
                        layer.on('click', () => {
                            this.showPrefectureInfo(prefName);
                        });

                        // ポップアップ設定
                        const prefData = this.prefectureData.get(prefName);
                        const count = prefData ? prefData.count24h : 0;
                        layer.bindPopup(`
                            <div style="color: #1a1a2e; text-align: center;">
                                <strong>${prefName}</strong><br>
                                過去24時間: <span style="color: #ff006e; font-weight: bold;">${count}件</span>
                            </div>
                        `);

                        // 境界線レイヤーを保存
                        this.prefectureBoundaries.set(prefName, layer);
                    }
                }
            }).addTo(this.map);

            console.log('✅ 都道府県境界線読み込み完了');

        } catch (error) {
            console.warn('都道府県境界線読み込み失敗:', error);
            // フォールバック: 簡易境界線を作成
            this.createSimpleBoundaries();
        }
    }

    createSimpleBoundaries() {
        // フォールバック用の簡易境界線
        console.log('📍 簡易境界線を作成中...');
        
        const majorPrefectures = [
            {name: '北海道', bounds: [[41.3, 139.4], [45.6, 148.0]]},
            {name: '東京都', bounds: [[35.5, 139.0], [36.0, 140.0]]},
            {name: '大阪府', bounds: [[34.3, 135.1], [34.8, 135.7]]},
            {name: '愛知県', bounds: [[34.5, 136.5], [35.4, 137.7]]},
            {name: '福岡県', bounds: [[33.0, 129.7], [34.0, 131.3]]}
        ];

        majorPrefectures.forEach(pref => {
            const rectangle = L.rectangle(pref.bounds, {
                color: 'rgba(0, 245, 255, 0.6)',
                weight: 2,
                fillOpacity: 0.1
            }).addTo(this.map);
            
            rectangle.bindPopup(`<strong>${pref.name}</strong>`);
            this.prefectureBoundaries.set(pref.name, rectangle);
        });
    }

    showPrefectureInfo(prefName) {
        const prefData = this.prefectureData.get(prefName);
        if (prefData) {
            const info = `
                📊 ${prefName} の統計
                過去24時間: ${prefData.count24h}件
                総投稿数: ${prefData.total || prefData.count24h * 7}件
                最終更新: ${prefData.lastUpdated.toLocaleTimeString()}
            `;
            alert(info);
        }
    }

    updatePrefectureBoundaryColors() {
        // 投稿数に応じて境界線の色を更新
        this.prefectureBoundaries.forEach((layer, prefName) => {
            this.updateSinglePrefectureColor(prefName, layer);
        });
    }

    updateSinglePrefectureColor(prefName, layer) {
        const prefData = this.prefectureData.get(prefName);
        if (prefData) {
            const count = prefData.count24h;
            let fillColor, borderColor, intensity;

            // 投稿数に応じた色分け（より明確に）
            if (count >= 100) {
                fillColor = 'rgba(255, 0, 110, 0.7)'; // 濃いピンク
                borderColor = '#ffffff';
                intensity = '激戦区';
            } else if (count >= 50) {
                fillColor = 'rgba(255, 133, 0, 0.6)'; // 濃いオレンジ
                borderColor = '#ffffff';
                intensity = '標準';
            } else if (count >= 20) {
                fillColor = 'rgba(0, 245, 255, 0.5)'; // 濃いブルー
                borderColor = '#ffffff';
                intensity = '平和';
            } else {
                fillColor = 'rgba(57, 255, 20, 0.4)'; // 濃いグリーン
                borderColor = '#ffffff';
                intensity = '超平和';
            }

            layer.setStyle({
                color: borderColor,
                fillColor: fillColor,
                weight: 3,
                opacity: 0.9,
                fillOpacity: 0.5,
                dashArray: '2, 4',
                lineCap: 'round',
                lineJoin: 'round'
            });

            // ポップアップ内容を更新（より詳細に）
            layer.bindPopup(`
                <div style="color: #1a1a2e; text-align: center; padding: 10px;">
                    <strong style="font-size: 1.1em;">${prefName}</strong><br>
                    <div style="margin: 5px 0;">
                        過去24時間: <span style="color: #ff006e; font-weight: bold; font-size: 1.2em;">${count}件</span>
                    </div>
                    <div style="background: ${fillColor}; padding: 3px 8px; border-radius: 12px; font-size: 0.9em;">
                        ${intensity}エリア
                    </div>
                </div>
            `);
        } else {
            // データがない場合のデフォルト表示
            layer.setStyle({
                color: '#ffffff',
                fillColor: 'rgba(128, 128, 128, 0.3)',
                weight: 3,
                opacity: 0.9,
                fillOpacity: 0.3,
                dashArray: '2, 4'
            });

            layer.bindPopup(`
                <div style="color: #1a1a2e; text-align: center;">
                    <strong>${prefName}</strong><br>
                    データ準備中...
                </div>
            `);
        }
    }

    async checkIPRestriction() {
        try {
            // ブラウザのローカルストレージで簡易IP制限
            const lastPostTime = localStorage.getItem('lastPostTime');
            const now = Date.now();
            const oneDayMs = 24 * 60 * 60 * 1000;

            if (lastPostTime && (now - parseInt(lastPostTime)) < oneDayMs) {
                return false;
            }

            // 実際の実装では、サーバーサイドでIPハッシュをチェック
            // const ipHash = await this.getIPHash();
            // const ipRef = this.database.ref(`ip_restrictions/${ipHash}`);
            // const snapshot = await ipRef.once('value');
            // return !snapshot.exists();

            return true;
        } catch (error) {
            console.error('IP制限チェックエラー:', error);
            return true; // エラー時は投稿を許可
        }
    }

    async createPostData() {
        const now = new Date();
        const timestamp = now.toISOString();
        
        // 位置情報の処理
        let locationData = {};
        if (this.userLocation.manual) {
            // 手動選択の場合
            locationData = {
                prefecture: this.userLocation.prefecture,
                type: 'manual'
            };
        } else {
            // GPS取得の場合
            locationData = {
                lat: Math.round(this.userLocation.lat * 100) / 100, // 精度を下げる
                lng: Math.round(this.userLocation.lng * 100) / 100,
                type: 'gps'
            };
            
            // 都道府県を逆算
            locationData.prefecture = await this.getPrefectureFromCoordinates(
                this.userLocation.lat, 
                this.userLocation.lng
            );
        }

        return {
            id: `post_${now.getTime()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: timestamp,
            location: locationData,
            userAgent: navigator.userAgent.substring(0, 100), // 匿名化済み
            hour: now.getHours(),
            dayOfWeek: now.getDay(),
            isWeekend: [0, 6].includes(now.getDay())
        };
    }

    async saveToFirebase(postData) {
        try {
            // 1. 投稿データを保存
            await this.postsRef.child(postData.id).set(postData);

            // 2. 都道府県統計を更新
            await this.updatePrefectureStats(postData.location.prefecture);

            // 3. 全体統計を更新
            await this.updateGlobalStats();

            // 4. ローカルストレージに投稿時刻を記録
            localStorage.setItem('lastPostTime', Date.now().toString());

        } catch (error) {
            console.error('Firebase保存エラー:', error);
            throw new Error('投稿の保存に失敗しました');
        }
    }

    async updatePrefectureStats(prefecture) {
        if (!prefecture) return;

        const prefRef = this.prefecturesRef.child(prefecture);
        const now = new Date();
        const today = now.toISOString().split('T')[0];

        try {
            // トランザクションで安全に更新
            await prefRef.transaction((currentData) => {
                if (currentData === null) {
                    // 新規作成
                    return {
                        name: prefecture,
                        total: 1,
                        today: {[today]: 1},
                        last24h: 1,
                        lastUpdated: now.toISOString()
                    };
                } else {
                    // 既存データ更新
                    currentData.total = (currentData.total || 0) + 1;
                    currentData.last24h = (currentData.last24h || 0) + 1;
                    
                    if (!currentData.today) {
                        currentData.today = {};
                    }
                    currentData.today[today] = (currentData.today[today] || 0) + 1;
                    currentData.lastUpdated = now.toISOString();
                    
                    return currentData;
                }
            });
        } catch (error) {
            console.error('都道府県統計更新エラー:', error);
        }
    }

    async updateGlobalStats() {
        const now = new Date();
        const today = now.toISOString().split('T')[0];

        try {
            await this.statisticsRef.transaction((currentData) => {
                if (currentData === null) {
                    return {
                        totalPosts: 1,
                        today: {[today]: 1},
                        last24h: 1,
                        lastUpdated: now.toISOString()
                    };
                } else {
                    currentData.totalPosts = (currentData.totalPosts || 0) + 1;
                    currentData.last24h = (currentData.last24h || 0) + 1;
                    
                    if (!currentData.today) {
                        currentData.today = {};
                    }
                    currentData.today[today] = (currentData.today[today] || 0) + 1;
                    currentData.lastUpdated = now.toISOString();
                    
                    return currentData;
                }
            });
        } catch (error) {
            console.error('全体統計更新エラー:', error);
        }
    }

    async getPrefectureFromCoordinates(lat, lng) {
        // 簡易的な座標から都道府県判定
        // 実際の実装では、より精密な逆ジオコーディングを使用
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1&accept-language=ja`
            );
            const data = await response.json();
            return data.address?.state || '不明';
        } catch (error) {
            console.warn('都道府県取得エラー:', error);
            return '不明';
        }
    }

    async submitHate() {
        const hateButton = document.getElementById('hateButton');
        
        if (!this.userLocation) {
            alert('位置情報を取得または都道府県を選択してからお試しください');
            return;
        }

        // ボタンを無効化
        hateButton.disabled = true;
        hateButton.textContent = '投稿中...';

        try {
            // IP制限チェック
            const canPost = await this.checkIPRestriction();
            if (!canPost) {
                throw new Error('本日はすでに投稿済みです。24時間後に再度お試しください。');
            }

            // 投稿データ作成
            const postData = await this.createPostData();
            
            // Firebaseに投稿
            await this.saveToFirebase(postData);
            
            console.log('✅ Firebase投稿完了:', postData);

            // 成功メッセージ
            hateButton.textContent = '投稿完了！';
            hateButton.style.background = '#27AE60';
            
            // 地図に新しいマーカー追加（デモ用）
            if (this.userLocation.manual) {
                // 手動選択の場合は都道府県中心にマーカー追加
                const center = this.getPrefectureCenter(this.userLocation.prefecture);
                if (center) {
                    this.addMarkerToMap(center.lat, center.lng, 1);
                }
            } else {
                // GPS取得の場合
                this.addMarkerToMap(this.userLocation.lat, this.userLocation.lng, 1);
            }
            
            // 統計は Firebase のリアルタイムリスナーで自動更新される

            // 24時間後に再投稿可能
            setTimeout(() => {
                hateButton.disabled = false;
                hateButton.textContent = '会社行きたくない！';
                hateButton.style.background = '';
            }, 3000); // デモでは3秒後に復活

        } catch (error) {
            console.error('投稿エラー:', error);
            hateButton.textContent = '投稿失敗';
            hateButton.disabled = false;
            alert('投稿に失敗しました。もう一度お試しください。');
        }
    }

    addMarkerToMap(lat, lng, count = 1) {
        // 既存マーカーを確認
        const key = `${lat.toFixed(3)}_${lng.toFixed(3)}`;
        
        if (this.markers.has(key)) {
            // 既存マーカーのカウント更新
            const existingMarker = this.markers.get(key);
            existingMarker.count += count;
            this.updateMarkerStyle(existingMarker);
        } else {
            // 新規マーカー作成
            const marker = L.circleMarker([lat, lng], {
                radius: this.getMarkerSize(count),
                fillColor: this.getMarkerColor(count),
                color: 'white',
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.7
            }).addTo(this.map);

            marker.count = count;
            marker.bindPopup(`この地域の投稿: ${count}件`);
            this.markers.set(key, marker);
        }
    }

    getMarkerSize(count) {
        return Math.min(8 + count * 3, 30);
    }

    getMarkerColor(count) {
        if (count <= 5) return '#4A90E2';      // 青
        if (count <= 15) return '#F39C12';     // 黄
        return '#E74C3C';                      // 赤
    }

    updateMarkerStyle(marker) {
        marker.setStyle({
            radius: this.getMarkerSize(marker.count),
            fillColor: this.getMarkerColor(marker.count)
        });
        marker.setPopupContent(`この地域の投稿: ${marker.count}件`);
    }

    initChart() {
        const ctx = document.getElementById('monthlyChart').getContext('2d');
        
        // 過去30日のデモデータ生成
        const labels = [];
        const data = [];
        const today = new Date();
        
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            labels.push(`${date.getMonth() + 1}/${date.getDate()}`);
            data.push(Math.floor(Math.random() * 100) + 20); // 20-120のランダム値
        }

        this.monthlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '日別投稿数',
                    data: data,
                    backgroundColor: 'rgba(0, 245, 255, 0.4)',
                    borderColor: '#00f5ff',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: '過去30日間の投稿数',
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            size: 16,
                            weight: 600
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            borderColor: 'rgba(255, 255, 255, 0.2)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)',
                            borderColor: 'rgba(255, 255, 255, 0.2)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: {
                                size: 11
                            }
                        },
                        title: {
                            display: true,
                            text: '投稿数',
                            color: 'rgba(255, 255, 255, 0.8)',
                            font: {
                                size: 12,
                                weight: 500
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }


    async setupRealtimeListeners() {
        try {
            // 1. 全体統計をリアルタイムで監視
            this.statisticsRef.on('value', (snapshot) => {
                const data = snapshot.val();
                this.updateStatsDisplay(data);
            });

            // 2. 都道府県データをリアルタイムで監視
            this.prefecturesRef.on('value', (snapshot) => {
                const data = snapshot.val();
                this.updatePrefectureData(data);
                this.updateRankings();
            });

            // 3. 投稿データをリアルタイムで監視（地図更新用）
            this.postsRef.limitToLast(100).on('child_added', (snapshot) => {
                const postData = snapshot.val();
                this.addPostToMap(postData);
            });

            console.log('🔄 リアルタイムリスナー設定完了');

            // 初期データが無い場合はデモデータを作成
            const statsSnapshot = await this.statisticsRef.once('value');
            if (!statsSnapshot.exists()) {
                console.log('📊 初期データが無いため、デモデータを作成します');
                await this.createInitialDemoData();
            }

        } catch (error) {
            console.error('リアルタイムリスナー設定エラー:', error);
            // エラー時はデモデータで代替
            this.loadFallbackDemoData();
        }
    }

    updateStatsDisplay(statsData) {
        if (!statsData) {
            document.getElementById('total24h').textContent = '0';
            document.getElementById('totalToday').textContent = '0';
            document.getElementById('totalThisMonth').textContent = '0';
            return;
        }

        const today = new Date().toISOString().split('T')[0];
        
        document.getElementById('total24h').textContent = statsData.last24h || 0;
        document.getElementById('totalToday').textContent = 
            (statsData.today && statsData.today[today]) || 0;
        document.getElementById('totalThisMonth').textContent = statsData.totalPosts || 0;
    }

    updatePrefectureData(prefecturesData) {
        this.prefectureData.clear();
        
        if (prefecturesData) {
            Object.entries(prefecturesData).forEach(([prefName, data]) => {
                this.prefectureData.set(prefName, {
                    count24h: data.last24h || 0,
                    total: data.total || 0,
                    lastUpdated: new Date(data.lastUpdated || Date.now())
                });
            });
        }

        console.log('📊 都道府県データ更新完了:', this.prefectureData.size);
        
        // 境界線の色を更新
        this.updatePrefectureBoundaryColors();
    }

    addPostToMap(postData) {
        if (!postData || !postData.location) return;

        let lat, lng;

        if (postData.location.type === 'manual') {
            // 手動選択の場合は都道府県中心座標を使用
            const center = this.getPrefectureCenter(postData.location.prefecture);
            if (!center) return;
            lat = center.lat;
            lng = center.lng;
        } else {
            // GPS座標を使用
            lat = postData.location.lat;
            lng = postData.location.lng;
        }

        // 地図にマーカーを追加
        this.addMarkerToMap(lat, lng, 1);
    }

    async createInitialDemoData() {
        // 現実的なデモデータを作成
        const prefectureProfiles = {
            // 超激戦区（平日朝の通勤ラッシュエリア）
            '東京都': { base: 180, variance: 40, factor: 1.3 }, // 140-220件 月曜は特に多い
            '大阪府': { base: 145, variance: 35, factor: 1.2 }, // 110-180件
            '神奈川県': { base: 125, variance: 30, factor: 1.2 }, // 95-155件
            '愛知県': { base: 110, variance: 25, factor: 1.1 }, // 85-135件
            '埼玉県': { base: 105, variance: 25, factor: 1.1 }, // 80-130件
            
            // 大都市圏（通勤者多数）
            '千葉県': { base: 85, variance: 20, factor: 1.1 }, // 65-105件
            '兵庫県': { base: 80, variance: 20, factor: 1.0 }, // 60-100件
            '北海道': { base: 75, variance: 25, factor: 0.9 }, // 50-100件（地方だが人口多い）
            '福岡県': { base: 70, variance: 20, factor: 1.0 }, // 50-90件
            '静岡県': { base: 55, variance: 15, factor: 1.0 }, // 40-70件
            
            // 中規模都市（そこそこ忙しい）
            '茨城県': { base: 45, variance: 15, factor: 1.0 }, // 30-60件
            '栃木県': { base: 40, variance: 12, factor: 1.0 }, // 28-52件
            '群馬県': { base: 42, variance: 13, factor: 1.0 }, // 29-55件
            '新潟県': { base: 48, variance: 15, factor: 0.9 }, // 33-63件
            '長野県': { base: 38, variance: 12, factor: 0.8 }, // 26-50件（自然豊かで平和）
            
            // 近畿圏（大阪周辺の通勤圏）
            '京都府': { base: 65, variance: 18, factor: 1.1 }, // 47-83件
            '奈良県': { base: 52, variance: 15, factor: 1.1 }, // 37-67件
            '滋賀県': { base: 45, variance: 12, factor: 1.0 }, // 33-57件
            '和歌山県': { base: 32, variance: 10, factor: 0.9 }, // 22-42件
            
            // 中部地方
            '富山県': { base: 35, variance: 10, factor: 0.9 }, // 25-45件（薬売り文化で温和？）
            '石川県': { base: 38, variance: 12, factor: 0.9 }, // 26-50件
            '福井県': { base: 30, variance: 8, factor: 0.8 }, // 22-38件（幸福度高い）
            '山梨県': { base: 35, variance: 10, factor: 0.9 }, // 25-45件
            '岐阜県': { base: 42, variance: 12, factor: 1.0 }, // 30-54件
            '三重県': { base: 45, variance: 12, factor: 1.0 }, // 33-57件
            
            // 中国・四国（地方都市）
            '広島県': { base: 58, variance: 15, factor: 1.0 }, // 43-73件
            '岡山県': { base: 48, variance: 12, factor: 1.0 }, // 36-60件
            '鳥取県': { base: 25, variance: 8, factor: 0.8 }, // 17-33件（人口少ない）
            '島根県': { base: 22, variance: 7, factor: 0.8 }, // 15-29件
            '山口県': { base: 38, variance: 10, factor: 0.9 }, // 28-48件
            '香川県': { base: 32, variance: 8, factor: 0.9 }, // 24-40件（うどん県で平和？）
            '徳島県': { base: 28, variance: 8, factor: 0.9 }, // 20-36件
            '愛媛県': { base: 35, variance: 10, factor: 0.9 }, // 25-45件
            '高知県': { base: 26, variance: 8, factor: 0.8 }, // 18-34件（のんびり）
            
            // 九州（地方だが福岡周辺は忙しい）
            '佐賀県': { base: 28, variance: 8, factor: 0.9 }, // 20-36件
            '長崎県': { base: 35, variance: 10, factor: 0.9 }, // 25-45件
            '熊本県': { base: 42, variance: 12, factor: 1.0 }, // 30-54件
            '大分県': { base: 35, variance: 10, factor: 0.9 }, // 25-45件（温泉でリラックス？）
            '宮崎県': { base: 30, variance: 8, factor: 0.8 }, // 22-38件（南国でのんびり）
            '鹿児島県': { base: 38, variance: 10, factor: 0.9 }, // 28-48件
            '沖縄県': { base: 20, variance: 8, factor: 0.7 }, // 12-28件（島時間でゆったり）
            
            // 東北（雪国で大変だが人情深い）
            '青森県': { base: 32, variance: 10, factor: 0.9 }, // 22-42件
            '岩手県': { base: 30, variance: 8, factor: 0.8 }, // 22-38件
            '宮城県': { base: 55, variance: 15, factor: 1.0 }, // 40-70件（仙台都市圏）
            '秋田県': { base: 25, variance: 8, factor: 0.8 }, // 17-33件
            '山形県': { base: 28, variance: 8, factor: 0.8 }, // 20-36件
            '福島県': { base: 38, variance: 12, factor: 0.9 }  // 26-50件
        };

        const batch = {};
        let totalPosts = 0;
        const today = new Date().toISOString().split('T')[0];
        const isMonday = new Date().getDay() === 1; // 月曜日は1.5倍
        const isFriday = new Date().getDay() === 5;  // 金曜日は0.8倍（週末前で気分良い）

        Object.entries(prefectureProfiles).forEach(([prefecture, profile]) => {
            // 基本投稿数を計算
            let count = profile.base + Math.floor((Math.random() - 0.5) * profile.variance * 2);
            
            // 曜日効果
            if (isMonday) count = Math.floor(count * 1.5); // 月曜ブルー
            if (isFriday) count = Math.floor(count * 0.8); // 金曜の解放感
            
            // 地域性ファクター適用
            count = Math.floor(count * profile.factor);
            
            // 時間帯によるリアルタイム変動（朝は多め）
            const hour = new Date().getHours();
            if (hour >= 7 && hour <= 9) count = Math.floor(count * 1.3); // 通勤ラッシュ
            if (hour >= 13 && hour <= 14) count = Math.floor(count * 1.1); // 昼休み後
            if (hour >= 22 || hour <= 5) count = Math.floor(count * 0.7); // 深夜早朝

            // 最低値保証
            count = Math.max(count, 5);

            batch[`prefectures/${prefecture}`] = {
                name: prefecture,
                total: count * 7, // 週間累計想定
                today: {[today]: count},
                last24h: count,
                lastUpdated: new Date().toISOString()
            };

            totalPosts += count;
        });

        // 全体統計
        batch['statistics'] = {
            totalPosts: totalPosts * 7, // 週間累計想定
            today: {[today]: totalPosts},
            last24h: totalPosts,
            lastUpdated: new Date().toISOString()
        };

        await this.database.ref().update(batch);
        console.log('✅ 現実的なデモデータ作成完了 - 総投稿数:', totalPosts);
    }

    loadFallbackDemoData() {
        // Firebase接続失敗時のフォールバック
        console.log('📊 フォールバックデモデータを読み込み中...');
        
        const isMonday = new Date().getDay() === 1;
        const hour = new Date().getHours();
        let multiplier = 1;
        
        if (isMonday) multiplier *= 1.5;
        if (hour >= 7 && hour <= 9) multiplier *= 1.3;
        
        // 現実的な統計表示
        const basePosts = Math.floor(2847 * multiplier);
        document.getElementById('total24h').textContent = basePosts.toLocaleString();
        document.getElementById('totalToday').textContent = Math.floor(basePosts * 0.6).toLocaleString();
        document.getElementById('totalThisMonth').textContent = (basePosts * 30).toLocaleString();

        // 現実的な都道府県データ（上位15位まで）
        const fallbackData = [
            ['東京都', Math.floor(234 * multiplier)], 
            ['大阪府', Math.floor(174 * multiplier)], 
            ['神奈川県', Math.floor(150 * multiplier)], 
            ['愛知県', Math.floor(121 * multiplier)], 
            ['埼玉県', Math.floor(115 * multiplier)],
            ['千葉県', Math.floor(94 * multiplier)],
            ['兵庫県', Math.floor(80 * multiplier)],
            ['北海道', Math.floor(68 * multiplier)],
            ['福岡県', Math.floor(70 * multiplier)],
            ['京都府', Math.floor(72 * multiplier)],
            ['静岡県', Math.floor(55 * multiplier)],
            ['宮城県', Math.floor(55 * multiplier)],
            ['広島県', Math.floor(58 * multiplier)],
            ['茨城県', Math.floor(45 * multiplier)],
            ['新潟県', Math.floor(43 * multiplier)]
        ];

        fallbackData.forEach(([pref, count]) => {
            this.prefectureData.set(pref, {
                count24h: count,
                total: count * 7,
                lastUpdated: new Date()
            });
        });

        // 地方都市のデータも追加（低めの数値）
        const ruralData = [
            '青森県', '岩手県', '秋田県', '山形県', '福島県', '栃木県', '群馬県',
            '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '三重県',
            '滋賀県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '山口県',
            '徳島県', '香川県', '愛媛県', '高知県', '佐賀県', '長崎県', '熊本県',
            '大分県', '宮崎県', '鹿児島県', '沖縄県'
        ];

        ruralData.forEach(pref => {
            const count = Math.floor((Math.random() * 25 + 15) * multiplier); // 15-40件程度
            this.prefectureData.set(pref, {
                count24h: count,
                total: count * 7,
                lastUpdated: new Date()
            });
        });

        this.updateRankings();
        
        // 主要都市にマーカーも追加
        const majorCityMarkers = [
            { lat: 35.6762, lng: 139.6503, count: Math.floor(15 * multiplier) }, // 東京
            { lat: 34.6937, lng: 135.5023, count: Math.floor(12 * multiplier) }, // 大阪
            { lat: 35.1815, lng: 136.9066, count: Math.floor(8 * multiplier) },  // 名古屋
            { lat: 35.4478, lng: 139.6425, count: Math.floor(10 * multiplier) }, // 横浜
            { lat: 33.5904, lng: 130.4017, count: Math.floor(6 * multiplier) },  // 福岡
            { lat: 43.0642, lng: 141.3469, count: Math.floor(4 * multiplier) },  // 札幌
            { lat: 38.2682, lng: 140.8694, count: Math.floor(3 * multiplier) },  // 仙台
            { lat: 34.3853, lng: 132.4553, count: Math.floor(5 * multiplier) },  // 広島
            { lat: 35.0116, lng: 135.7681, count: Math.floor(5 * multiplier) },  // 京都
        ];

        majorCityMarkers.forEach(marker => {
            this.addMarkerToMap(marker.lat, marker.lng, marker.count);
        });
    }

    initRankings() {
        // スマホタブ切り替え機能
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // アクティブクラス切り替え
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
            });
        });
    }


    updateRankings() {
        // 都道府県データをソート
        const sortedData = Array.from(this.prefectureData.entries())
            .sort((a, b) => b[1].count24h - a[1].count24h);

        // ベスト5（投稿数が多い = 行きたくない度が高い）
        const bestFive = sortedData.slice(0, 5);
        
        // ワースト5（投稿数が少ない = 平和度が高い）
        const worstFive = sortedData.slice(-5).reverse();

        // PC版ランキング更新
        this.renderRanking('bestRanking', bestFive, 'best');
        this.renderRanking('worstRanking', worstFive, 'worst');
        
        // スマホ版ランキング更新  
        this.renderRanking('mobileBestRanking', bestFive, 'best');
        this.renderRanking('mobileWorstRanking', worstFive, 'worst');
    }

    renderRanking(containerId, data, type) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        data.forEach((item, index) => {
            const [prefecture, info] = item;
            const rank = index + 1;
            
            const li = document.createElement('li');
            li.className = 'ranking-item';
            
            // ランク番号の絵文字
            const rankEmoji = type === 'best' 
                ? ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][index] 
                : ['🏆', '🎉', '✨', '🌸', '🍀'][index];
            
            li.innerHTML = `
                <span class="ranking-rank">${rankEmoji}</span>
                <span class="ranking-prefecture">${prefecture}</span>
                <span class="ranking-count">${info.count24h}件</span>
            `;
            
            container.appendChild(li);
        });
    }
}

// SNS共有機能
function shareToTwitter() {
    const text = '会社行きたくないメーター 📊 みんなの「行きたくない」気持ちをリアルタイム共有中！ #会社行きたくない #ストレス発散';
    const url = window.location.href;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=400');
}

function shareToLine() {
    const text = '会社行きたくないメーター - 全国の「行きたくない」をリアルタイム共有';
    const url = window.location.href;
    const lineUrl = `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(lineUrl, '_blank', 'width=600,height=400');
}

// Google Analytics (後で設定)
// gtag('config', 'GA_MEASUREMENT_ID');

// アプリケーション開始
document.addEventListener('DOMContentLoaded', () => {
    new CompanyHateMeter();
});