let scene, camera, renderer, characters = [], mixers = [];
let clock;
const floorWidth = 30;
const floorDepth = 18.5;
const safetyMult = 1.5;
const numCharacters = 30;
const numInfected = 2;
const percentageWidth = 1;
const aspectRatio = 16 / 9;
const infectionProbability = 0.5;
const recoveryTime = 10000;
let speed = 3;
let infectedSpeed = 4;
const scale = 1;

speed = (speed * scale).toFixed(1);
infectedSpeed = (infectedSpeed * scale).toFixed(1);

let simulationTime = [];
let healthyCounts = [];
let infectedCounts = [];
let recoveredCounts = [];
let simulationStartTime = Date.now();
let simulationRunning = true;
let frameCount = 0;

function calculateInitialXPosition(index) {
    return -floorWidth / 2 + safetyMult * scale + index * (floorWidth - 2 * safetyMult * scale) / (numCharacters - 1);
}

function calculateInitialZPosition() {
    return -floorDepth / 2 + safetyMult * scale + Math.random() * (floorDepth - 2 * safetyMult * scale);
}

function setupChart(ctx) {
    window.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: simulationTime,
            datasets: [{
                label: 'Healthy',
                data: healthyCounts,
                borderColor: '#8E9A9D',
                backgroundColor: 'rgba(142, 154, 157, 0.6)',
                pointRadius: 0,
                borderWidth: 2,
                fill: true
            }, {
                label: 'Infected',
                data: infectedCounts,
                borderColor: '#417E37',
                backgroundColor: 'rgba(65, 126, 55, 0.6)',
                pointRadius: 0,
                borderWidth: 2,
                fill: true
            }, {
                label: 'Recovered',
                data: recoveredCounts,
                borderColor: '#3A80BA',
                backgroundColor: 'rgba(58, 128, 186, 0.6)',
                pointRadius:0,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time (seconds)',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        display: false,
                    }
                },
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: numCharacters,
                    title: {
                        display: true,
                        text: 'Number of people',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        display: false,
                    }
                }
            },
            plugins: {
                tooltip: {
                    enabled: false,
                },
                legend: {
                    position: 'top',
                    labels: {
                        color: '#fff'
                    }
                }
            },
            animation: {
                duration: 0.5,
            },
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function updateChart(currentTime, healthy, infected, recovered) {
    simulationTime.push(currentTime / 1000);
    healthyCounts.push(healthy);
    infectedCounts.push(infected);
    recoveredCounts.push(recovered);

    if (simulationTime.length % 5 === 0) {
        chart.data.labels = simulationTime;
        chart.data.datasets[0].data = healthyCounts;
        chart.data.datasets[1].data = infectedCounts;
        chart.data.datasets[2].data = recoveredCounts;

        let maxXValue = Math.max(...simulationTime);
        chart.options.scales.x.max = maxXValue;
        chart.update();
    }
}

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, aspectRatio, 0.1, 1000);
    camera.position.set(0, 16, 16);
    camera.lookAt(new THREE.Vector3(0, 0, 0));

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setClearColor(0x111729, 1);
    const container = document.getElementById('canvas-container');
    width = container.clientWidth * percentageWidth;
    height = width / aspectRatio;
    renderer.setSize(width, height);
    updateRendererSize();
    document.body.appendChild(renderer.domElement);

    container.appendChild(renderer.domElement);

    const chartCanvas = document.createElement('canvas');
    chartCanvas.id = 'chart-canvas';
    container.appendChild(chartCanvas);

    const light = new THREE.HemisphereLight(0xffffbb, 0x080820, 8);
    scene.add(light);

    const groundGeometry = new THREE.PlaneGeometry(floorWidth, floorDepth);
    const groundMaterial = new THREE.MeshLambertMaterial({ color: 0xCCCCCC });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1;
    scene.add(ground);

    clock = new THREE.Clock(); 
    setupChart(chartCanvas.getContext('2d'));

    for (let i = 0; i < numCharacters; i++) {
        let xPosition = calculateInitialXPosition(i);
        let zPosition = calculateInitialZPosition();
        let healthState = i < numInfected ? 1 : 0;
        loadModel(xPosition, zPosition, i, healthState);
    }

    window.addEventListener('resize', onWindowResize, false);

    animate();
}

function loadModel(xPosition, zPosition, index, healthState) {
    const folderNames = ['healthy', 'infected', 'recovered'];
    const stateFolder = folderNames[healthState];
    const loader = new THREE.GLTFLoader();

    loader.load(`../images/posts/${stateFolder}/scene.gltf`, function (gltf) {
        const character = gltf.scene;
        const boundingBox = new THREE.Box3().setFromObject(character);
        const size = new THREE.Vector3();
        boundingBox.getSize(size);

        // console.log("Width:", size.x);
        // console.log("Height:", size.y);
        // console.log("Depth:", size.z);

        character.scale.set(scale, scale, scale);
        character.position.set(xPosition, 0, zPosition);
        character.rotation.y = Math.random() * 2 * Math.PI;
        scene.add(character);

        if (characters[index]) {
            scene.remove(characters[index]);
            mixers[index].uncacheRoot(characters[index]);
        }

        characters[index] = character;
        if (healthState === 1) {
            characters[index].speed = infectedSpeed;
        } else {
            characters[index].speed = speed;
        }
        characters[index].healthState = healthState;
        characters[index].height = size.y * scale;
        characters[index].width = size.x * scale;
        characters[index].depth = size.z * scale;

        const mixer = new THREE.AnimationMixer(character);
        mixers[index] = mixer;

        const clip = THREE.AnimationClip.findByName(gltf.animations, 'Walk');
        if (clip) {
            const action = mixer.clipAction(clip);
            action.play();
        }

        // Set a (recovery) timer if the character is initially infected
        if (healthState === 1) {
            setTimeout(() => {
                if (characters[index].healthState === 1) {
                    updateHealthState(index, 2);
                }
            }, recoveryTime);
        }
    }, undefined, function (error) {
        console.error('An error happened loading the model:', error);
    });
}

function animate() {
    if (!simulationRunning) {
        return;
    }

    requestAnimationFrame(animate);

    // Cap the delta time to at most 0.1s to avoid erratic behavior upon browser tab changes!
    const delta = Math.min(clock.getDelta(), 0.1);

    healthyCount = 0;
    infectedCount = 0;
    recoveredCount = 0;

    characters.forEach(character => {
        updatePosition(character, delta);
        if (character.healthState === 0) {
            healthyCount++;
        } else if (character.healthState === 1) {
            infectedCount++;
        } else if (character.healthState === 2) {
            recoveredCount++;
        }
    });

    mixers.forEach(mixer => {
        if (mixer) mixer.update(delta);
    });

    checkCollisions();
    checkCharacterCollisions();

    updateChart(performance.now(), healthyCount, infectedCount, recoveredCount);

    renderer.render(scene, camera);

    frameCount++;
    if (frameCount > 10 && infectedCount === 0) {
        simulationRunning = false;
    }
    updateOverlayInfo();
}

function updateOverlayInfo() {
    document.getElementById('total-count').textContent = characters.length;
    document.getElementById('healthy-count').textContent = characters.filter(c => c.healthState === 0).length;
    document.getElementById('infected-count').textContent = characters.filter(c => c.healthState === 1).length;
    document.getElementById('recovered-count').textContent = characters.filter(c => c.healthState === 2).length;
    document.getElementById('prob-infected').textContent = infectionProbability * 100;
    document.getElementById('recovery-time').textContent = recoveryTime / 1000;
    // document.getElementById('time-elapsed').textContent = ((Date.now() - simulationStartTime) / 1000).toFixed(1);
    document.getElementById('normal-speed').textContent = speed;
    document.getElementById('infected-speed').textContent = infectedSpeed;
}

function updatePosition(character, delta) {
    const forward = new THREE.Vector3(0, 0, 1);
    forward.applyQuaternion(character.quaternion);
    character.position.addScaledVector(forward, character.speed * delta);
}

function checkCollisions() {
    const halfFloorWidth = floorWidth / 2;
    const halfFloorDepth = floorDepth / 2;

    characters.forEach(character => {
        let collisionDetected = false;
        let rotateAmount = null;
        let collisionWall = null;

        if (character.position.x - character.width / 2 < -halfFloorWidth) {
            rotateAmount = Math.PI / 2 + (Math.random() * Math.PI / 2 - Math.PI / 4);
            collisionDetected = true;
            collisionWall = 'left';
            // console.log('-Half floor width', -halfFloorWidth);
            // console.log('Character width', character.width);
            // console.log('Character position x', character.position.x);
        }
        
        else if (character.position.x + character.width / 2 > halfFloorWidth) {
            rotateAmount = 3 * Math.PI / 2 + (Math.random() * Math.PI / 2 - Math.PI / 4);
            collisionDetected = true;
            collisionWall = 'right';
            // console.log('Half floor width', halfFloorWidth);
            // console.log('Character width', character.width);
            // console.log('Character position x', character.position.x);
        }

        else if (character.position.z - character.depth < -halfFloorDepth) {
            rotateAmount = (Math.random() * Math.PI / 2 - Math.PI / 4);
            collisionDetected = true;
            collisionWall = 'far';
            // console.log('-Half floor depth', -halfFloorDepth);
            // console.log('Character depth', character.depth);
            // console.log('Character position z', character.position.z);
        }
        
        else if (character.position.z  > halfFloorDepth) {
            rotateAmount = Math.PI + (Math.random() * Math.PI / 2 - Math.PI / 4);
            collisionDetected = true;
            collisionWall = 'near';
            // console.log('Half floor depth', halfFloorDepth);
            // console.log('Character depth', character.depth);
            // console.log('Character position z', character.position.z);
        }

        if (collisionDetected) {
            character.rotation.y = rotateAmount;
        }
    });
}

function updateHealthState(index, newHealthState) {
    if (newHealthState === 1) {
        characters[index].healthState = newHealthState;
        setTimeout(() => {
            // console.log(`Character ${index} has recovered!`);
            if (characters[index].healthState === 1) {
                updateHealthState(index, 2);
            }
        }, recoveryTime);
    } else {
        characters[index].healthState = newHealthState;
    }
    loadModel(characters[index].position.x, characters[index].position.z, index, newHealthState);
}

function checkCharacterCollisions() {
    characters.forEach((charA, idxA) => {
        characters.forEach((charB, idxB) => {
            if (idxA !== idxB) {
                const dx = charA.position.x - charB.position.x;
                const dz = charA.position.z - charB.position.z;
                const distance = Math.sqrt(dx * dx + dz * dz);
                const collisionDistance = 1 * safetyMult * scale;
                if (distance < collisionDistance) {
                    if (charA.healthState === 0 && charB.healthState === 1) {
                        if (Math.random() < infectionProbability) {
                            updateHealthState(idxA, 1);
                        }
                    } else if (charB.healthState === 0 && charA.healthState === 1) {
                        if (Math.random() < infectionProbability) {
                            updateHealthState(idxB, 1);
                        }
                    }
                    const angle = Math.atan2(dz, dx);
                    const randomAdjustment = Math.PI / 8 * (Math.random() - 0.5) * 2; // add +/- 22.5 degree random adjustment
                    charA.rotation.y = angle + Math.PI + randomAdjustment; // A turns roughly away from B
                    charB.rotation.y = angle + randomAdjustment; // B turns roughly away from A
                    charA.rotation.y = angle + Math.PI;
                }
            }
        });
    });
}

function updateRendererSize() {
    const container = document.getElementById('canvas-container');
    width = container.clientWidth * percentageWidth;
    height = width / aspectRatio;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
}

function onWindowResize() {
    updateRendererSize();
}

window.onload = function() {
    const container = document.getElementById('canvas-container');
    if (!container) {
        console.log('Canvas container not found, skipping loading scripts.');
        return;
    } else {
        loadScript('https://unpkg.com/three@0.108.0/build/three.js', function() {
            console.log('THREE.js loaded successfully!');

            loadScript('https://unpkg.com/three@0.108.0/examples/js/loaders/GLTFLoader.js', function() {
                console.log('GLTFLoader loaded successfully!');

                loadScript('https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js', function() {
                    console.log('Tween.js loaded successfully!');

                    loadScript('https://cdn.jsdelivr.net/npm/@loaders.gl/core/dist/dist.min.js', function() {
                        console.log('@loaders.gl/core loaded successfully!');

                        loadScript('https://cdn.jsdelivr.net/npm/@loaders.gl/gltf/dist/dist.min.js', function() {
                            console.log('@loaders.gl/gltf loaded successfully!');

                            loadScript('https://cdn.jsdelivr.net/npm/chart.js', function() {
                                console.log('Chart.js loaded successfully!');
                                init();
                            });
                        });
                    });
                });
            });
        });
    }
    window.addEventListener('resize', onWindowResize, false);
};

function loadScript(url, callback) {
    const script = document.createElement('script');
    script.src = url;
    script.onload = callback;
    script.onerror = function() {
        console.error('Error loading script:', url);
    };
    document.head.appendChild(script);
}



