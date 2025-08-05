class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        
        // 游戏状态
        this.gameState = 'start'; // start, playing, paused, gameOver
        this.score = 0;
        this.level = 1;
        this.lives = 3;
        
        // 玩家飞机
        this.player = {
            x: this.width / 2,
            y: this.height - 100,
            width: 40,
            height: 40,
            speed: 5,
            bullets: [],
            lastShot: 0,
            shotCooldown: 200,
            powerUps: {
                rapidFire: 0,
                shield: 0
            }
        };
        
        // 敌人
        this.enemies = [];
        this.enemySpawnTimer = 0;
        this.enemySpawnRate = 1000;
        
        // 粒子效果
        this.particles = [];
        this.explosions = [];
        
        // 背景
        this.stars = [];
        this.clouds = [];
        
        // 输入处理
        this.keys = {};
        this.setupEventListeners();
        
        // 音效
        this.setupAudio();
        
        // 初始化背景
        this.initBackground();
        
        // 开始游戏循环
        this.gameLoop();
    }
    
    setupEventListeners() {
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            
            if (e.code === 'Escape' && this.gameState === 'playing') {
                this.pauseGame();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
        
        // 按钮事件
        document.getElementById('startButton').addEventListener('click', () => {
            this.startGame();
        });
        
        document.getElementById('resumeButton').addEventListener('click', () => {
            this.resumeGame();
        });
        
        document.getElementById('restartButton').addEventListener('click', () => {
            this.restartGame();
        });
        
        document.getElementById('playAgainButton').addEventListener('click', () => {
            this.restartGame();
        });
    }
    
    setupAudio() {
        // 创建音效上下文
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // 音效函数
        this.playSound = (frequency, duration, type = 'sine') => {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
            oscillator.type = type;
            
            gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }
    
    initBackground() {
        // 创建星星
        for (let i = 0; i < 100; i++) {
            this.stars.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                size: Math.random() * 2 + 1,
                speed: Math.random() * 2 + 1
            });
        }
        
        // 创建云朵
        for (let i = 0; i < 5; i++) {
            this.clouds.push({
                x: Math.random() * this.width,
                y: Math.random() * (this.height / 2),
                width: Math.random() * 100 + 50,
                height: Math.random() * 30 + 20,
                speed: Math.random() * 0.5 + 0.2
            });
        }
    }
    
    startGame() {
        this.gameState = 'playing';
        this.hideScreen('startScreen');
        this.resetGame();
    }
    
    pauseGame() {
        this.gameState = 'paused';
        this.showScreen('pauseScreen');
    }
    
    resumeGame() {
        this.gameState = 'playing';
        this.hideScreen('pauseScreen');
    }
    
    gameOver() {
        this.gameState = 'gameOver';
        document.getElementById('finalScore').textContent = this.score;
        document.getElementById('finalLevel').textContent = this.level;
        this.showScreen('gameOverScreen');
    }
    
    restartGame() {
        this.resetGame();
        this.gameState = 'playing';
        this.hideAllScreens();
    }
    
    resetGame() {
        this.score = 0;
        this.level = 1;
        this.lives = 3;
        this.player.x = this.width / 2;
        this.player.y = this.height - 100;
        this.player.bullets = [];
        this.player.powerUps.rapidFire = 0;
        this.player.powerUps.shield = 0;
        this.enemies = [];
        this.particles = [];
        this.explosions = [];
        this.updateUI();
    }
    
    hideScreen(screenId) {
        document.getElementById(screenId).classList.add('hidden');
    }
    
    showScreen(screenId) {
        document.getElementById(screenId).classList.remove('hidden');
    }
    
    hideAllScreens() {
        document.querySelectorAll('.screen-overlay').forEach(screen => {
            screen.classList.add('hidden');
        });
    }
    
    updateUI() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('level').textContent = this.level;
        document.getElementById('lives').textContent = this.lives;
        document.getElementById('rapidFire').textContent = Math.ceil(this.player.powerUps.rapidFire / 1000);
        document.getElementById('shield').textContent = Math.ceil(this.player.powerUps.shield / 1000);
    }
    
    updatePlayer() {
        // 移动玩家
        if (this.keys['ArrowLeft'] && this.player.x > 0) {
            this.player.x -= this.player.speed;
        }
        if (this.keys['ArrowRight'] && this.player.x < this.width - this.player.width) {
            this.player.x += this.player.speed;
        }
        if (this.keys['ArrowUp'] && this.player.y > 0) {
            this.player.y -= this.player.speed;
        }
        if (this.keys['ArrowDown'] && this.player.y < this.height - this.player.height) {
            this.player.y += this.player.speed;
        }
        
        // 射击
        if (this.keys['Space']) {
            const now = Date.now();
            const cooldown = this.player.powerUps.rapidFire > 0 ? 100 : this.player.shotCooldown;
            
            if (now - this.player.lastShot > cooldown) {
                this.shoot();
                this.player.lastShot = now;
            }
        }
        
        // 更新道具
        if (this.player.powerUps.rapidFire > 0) {
            this.player.powerUps.rapidFire -= 16;
        }
        if (this.player.powerUps.shield > 0) {
            this.player.powerUps.shield -= 16;
        }
    }
    
    shoot() {
        const bullet = {
            x: this.player.x + this.player.width / 2 - 2,
            y: this.player.y,
            width: 4,
            height: 10,
            speed: 8
        };
        
        this.player.bullets.push(bullet);
        this.playSound(800, 0.1, 'square');
    }
    
    spawnEnemy() {
        const enemy = {
            x: Math.random() * (this.width - 40),
            y: -40,
            width: 40,
            height: 40,
            speed: Math.random() * 2 + 1 + this.level * 0.5,
            health: 1 + Math.floor(this.level / 3)
        };
        
        this.enemies.push(enemy);
    }
    
    updateEnemies() {
        this.enemySpawnTimer += 16;
        if (this.enemySpawnTimer > this.enemySpawnRate) {
            this.spawnEnemy();
            this.enemySpawnTimer = 0;
            this.enemySpawnRate = Math.max(200, 1000 - this.level * 50);
        }
        
        this.enemies.forEach((enemy, index) => {
            enemy.y += enemy.speed;
            
            if (enemy.y > this.height) {
                this.enemies.splice(index, 1);
            }
        });
    }
    
    updateBullets() {
        this.player.bullets.forEach((bullet, bulletIndex) => {
            bullet.y -= bullet.speed;
            
            if (bullet.y < 0) {
                this.player.bullets.splice(bulletIndex, 1);
            }
        });
    }
    
    checkCollisions() {
        // 子弹与敌人碰撞
        this.player.bullets.forEach((bullet, bulletIndex) => {
            this.enemies.forEach((enemy, enemyIndex) => {
                if (this.isColliding(bullet, enemy)) {
                    enemy.health--;
                    this.player.bullets.splice(bulletIndex, 1);
                    
                    if (enemy.health <= 0) {
                        this.enemies.splice(enemyIndex, 1);
                        this.score += 100;
                        this.createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2);
                        this.playSound(400, 0.2, 'sawtooth');
                        
                        // 随机掉落道具
                        if (Math.random() < 0.1) {
                            this.createPowerUp(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2);
                        }
                    }
                }
            });
        });
        
        // 玩家与敌人碰撞
        this.enemies.forEach((enemy, index) => {
            if (this.isColliding(this.player, enemy)) {
                if (this.player.powerUps.shield <= 0) {
                    this.lives--;
                    this.createExplosion(this.player.x + this.player.width / 2, this.player.y + this.player.height / 2);
                    this.playSound(200, 0.3, 'triangle');
                    
                    if (this.lives <= 0) {
                        this.gameOver();
                    }
                }
                this.enemies.splice(index, 1);
            }
        });
        
        // 检查等级提升
        if (this.score >= this.level * 1000) {
            this.level++;
            this.playSound(600, 0.5, 'sine');
        }
    }
    
    isColliding(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }
    
    createExplosion(x, y) {
        for (let i = 0; i < 20; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                life: 60,
                maxLife: 60,
                color: `hsl(${Math.random() * 60 + 15}, 100%, 50%)`
            });
        }
    }
    
    createPowerUp(x, y) {
        const powerUp = {
            x: x,
            y: y,
            width: 20,
            height: 20,
            type: Math.random() < 0.5 ? 'rapidFire' : 'shield',
            speed: 2
        };
        
        this.powerUps = this.powerUps || [];
        this.powerUps.push(powerUp);
    }
    
    updateParticles() {
        this.particles.forEach((particle, index) => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.life--;
            
            if (particle.life <= 0) {
                this.particles.splice(index, 1);
            }
        });
    }
    
    updatePowerUps() {
        if (!this.powerUps) return;
        
        this.powerUps.forEach((powerUp, index) => {
            powerUp.y += powerUp.speed;
            
            if (powerUp.y > this.height) {
                this.powerUps.splice(index, 1);
            }
            
            // 检查玩家收集道具
            if (this.isColliding(this.player, powerUp)) {
                if (powerUp.type === 'rapidFire') {
                    this.player.powerUps.rapidFire = 10000; // 10秒
                } else if (powerUp.type === 'shield') {
                    this.player.powerUps.shield = 8000; // 8秒
                }
                this.powerUps.splice(index, 1);
                this.playSound(1000, 0.2, 'sine');
            }
        });
    }
    
    updateBackground() {
        // 更新星星
        this.stars.forEach(star => {
            star.y += star.speed;
            if (star.y > this.height) {
                star.y = -5;
                star.x = Math.random() * this.width;
            }
        });
        
        // 更新云朵
        this.clouds.forEach(cloud => {
            cloud.x += cloud.speed;
            if (cloud.x > this.width + cloud.width) {
                cloud.x = -cloud.width;
                cloud.y = Math.random() * (this.height / 2);
            }
        });
    }
    
    drawBackground() {
        // 绘制渐变背景
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height);
        gradient.addColorStop(0, '#000428');
        gradient.addColorStop(1, '#004e92');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // 绘制星星
        this.ctx.fillStyle = '#ffffff';
        this.stars.forEach(star => {
            this.ctx.globalAlpha = Math.random() * 0.8 + 0.2;
            this.ctx.fillRect(star.x, star.y, star.size, star.size);
        });
        this.ctx.globalAlpha = 1;
        
        // 绘制云朵
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        this.clouds.forEach(cloud => {
            this.ctx.fillRect(cloud.x, cloud.y, cloud.width, cloud.height);
        });
    }
    
    drawPlayer() {
        // 绘制护盾效果
        if (this.player.powerUps.shield > 0) {
            this.ctx.strokeStyle = '#00ffff';
            this.ctx.lineWidth = 3;
            this.ctx.globalAlpha = 0.5;
            this.ctx.beginPath();
            this.ctx.arc(this.player.x + this.player.width / 2, this.player.y + this.player.height / 2, 
                         this.player.width / 2 + 10, 0, Math.PI * 2);
            this.ctx.stroke();
            this.ctx.globalAlpha = 1;
        }
        
        // 绘制玩家飞机
        this.ctx.fillStyle = '#00ff00';
        this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        
        // 绘制飞机细节
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(this.player.x + 5, this.player.y + 5, 30, 30);
        this.ctx.fillStyle = '#ff0000';
        this.ctx.fillRect(this.player.x + 10, this.player.y + 10, 20, 20);
    }
    
    drawEnemies() {
        this.ctx.fillStyle = '#ff0000';
        this.enemies.forEach(enemy => {
            this.ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
            
            // 绘制敌人细节
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fillRect(enemy.x + 5, enemy.y + 5, 30, 30);
            this.ctx.fillStyle = '#000000';
            this.ctx.fillRect(enemy.x + 10, enemy.y + 10, 20, 20);
        });
    }
    
    drawBullets() {
        this.ctx.fillStyle = '#ffff00';
        this.player.bullets.forEach(bullet => {
            this.ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
        });
    }
    
    drawParticles() {
        this.particles.forEach(particle => {
            this.ctx.fillStyle = particle.color;
            this.ctx.globalAlpha = particle.life / particle.maxLife;
            this.ctx.fillRect(particle.x, particle.y, 3, 3);
        });
        this.ctx.globalAlpha = 1;
    }
    
    drawPowerUps() {
        if (!this.powerUps) return;
        
        this.powerUps.forEach(powerUp => {
            if (powerUp.type === 'rapidFire') {
                this.ctx.fillStyle = '#ffff00';
            } else {
                this.ctx.fillStyle = '#00ffff';
            }
            this.ctx.fillRect(powerUp.x, powerUp.y, powerUp.width, powerUp.height);
        });
    }
    
    render() {
        this.drawBackground();
        this.drawPlayer();
        this.drawEnemies();
        this.drawBullets();
        this.drawParticles();
        this.drawPowerUps();
    }
    
    update() {
        if (this.gameState !== 'playing') return;
        
        this.updatePlayer();
        this.updateEnemies();
        this.updateBullets();
        this.updateParticles();
        this.updatePowerUps();
        this.updateBackground();
        this.checkCollisions();
        this.updateUI();
    }
    
    gameLoop() {
        this.update();
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// 启动游戏
window.addEventListener('load', () => {
    new Game();
});