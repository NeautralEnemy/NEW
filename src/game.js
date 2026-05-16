import * as THREE from 'https://unpkg.com/three@0.164.1/build/three.module.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060a13);
scene.fog = new THREE.Fog(0x060a13, 30, 95);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 250);
camera.position.set(0, 1.7, 16);

const hemi = new THREE.HemisphereLight(0x99bbff, 0x1c2432, 0.8);
scene.add(hemi);
const dir = new THREE.DirectionalLight(0xffffff, 0.8);
dir.position.set(-12, 18, 9);
scene.add(dir);

const arenaRadius = 28;
const floor = new THREE.Mesh(
  new THREE.CylinderGeometry(arenaRadius, arenaRadius, 1.2, 64),
  new THREE.MeshStandardMaterial({ color: 0x111c29, metalness: 0.2, roughness: 0.85 })
);
floor.position.y = -0.6;
scene.add(floor);

const wall = new THREE.Mesh(
  new THREE.CylinderGeometry(arenaRadius + 0.8, arenaRadius + 0.8, 8, 64, 1, true),
  new THREE.MeshStandardMaterial({ color: 0x1e2c40, side: THREE.DoubleSide, emissive: 0x0a1020 })
);
wall.position.y = 3;
scene.add(wall);

const ring = new THREE.Mesh(
  new THREE.TorusGeometry(arenaRadius, 0.24, 16, 90),
  new THREE.MeshStandardMaterial({ color: 0x7eb3ff, emissive: 0x2f5faa })
);
ring.rotation.x = Math.PI / 2;
ring.position.y = 0.02;
scene.add(ring);

const pillars = [];
for (let i = 0; i < 12; i++) {
  const a = (i / 12) * Math.PI * 2;
  const r = 15 + (i % 2) * 5;
  const p = new THREE.Mesh(
    new THREE.CylinderGeometry(1.2, 1.2, 6, 12),
    new THREE.MeshStandardMaterial({ color: 0x152334, roughness: 0.9 })
  );
  p.position.set(Math.cos(a) * r, 3, Math.sin(a) * r);
  scene.add(p);
  pillars.push(p);
}

const state = {
  hp: 100,
  score: 0,
  round: 1,
  fireCooldown: 0,
  hitCooldown: 0,
  bobTime: 0,
  gameOver: false,
};

const keys = new Set();
let yaw = Math.PI;
let pitch = -0.05;
let mouseDown = false;
const velocity = new THREE.Vector3();
const enemies = [];
const bullets = [];

const hpEl = document.getElementById('hp');
const roundEl = document.getElementById('round');
const enemiesEl = document.getElementById('enemies');
const scoreEl = document.getElementById('score');
const centerMessage = document.getElementById('centerMessage');
const hitFlash = document.getElementById('hitFlash');

function updateHud() {
  hpEl.textContent = Math.max(0, Math.floor(state.hp));
  roundEl.textContent = state.round;
  enemiesEl.textContent = enemies.length;
  scoreEl.textContent = state.score;
}

function spawnRound(round) {
  const count = 4 + round * 2;
  for (let i = 0; i < count; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = 8 + Math.random() * (arenaRadius - 6);
    const enemy = new THREE.Mesh(
      new THREE.SphereGeometry(0.8 + Math.min(round * 0.05, 0.6), 14, 12),
      new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.0 + Math.random() * 0.06, 0.8, 0.55),
        emissive: 0x330909,
      })
    );
    enemy.position.set(Math.cos(a) * r, 0.9, Math.sin(a) * r);
    enemy.userData = {
      hp: 16 + round * 5,
      speed: 2.2 + round * 0.17,
      damage: 8 + round,
      hitTimer: 0,
    };
    enemies.push(enemy);
    scene.add(enemy);
  }
  updateHud();
}

function restart() {
  for (const e of enemies) scene.remove(e);
  for (const b of bullets) scene.remove(b.mesh);
  enemies.length = 0;
  bullets.length = 0;
  state.hp = 100;
  state.score = 0;
  state.round = 1;
  state.gameOver = false;
  centerMessage.style.display = 'none';
  spawnRound(1);
}

function shoot() {
  if (state.fireCooldown > 0 || state.gameOver) return;
  state.fireCooldown = 0.16;

  const dir = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ')).normalize();
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 8, 8),
    new THREE.MeshStandardMaterial({ color: 0xa9d5ff, emissive: 0x3f7ac3 })
  );
  mesh.position.copy(camera.position).addScaledVector(dir, 0.55);
  scene.add(mesh);

  bullets.push({ mesh, dir, speed: 58, ttl: 1.3 });
}

function onEnemyKilled(enemy) {
  scene.remove(enemy);
  const idx = enemies.indexOf(enemy);
  if (idx >= 0) enemies.splice(idx, 1);
  state.score += 10 + state.round * 3;

  if (enemies.length === 0) {
    state.round += 1;
    centerMessage.style.display = 'block';
    centerMessage.innerHTML = `Round ${state.round - 1} cleared!<br/>Next wave in 1.5s`;
    setTimeout(() => {
      if (!state.gameOver) {
        centerMessage.style.display = 'none';
        spawnRound(state.round);
      }
    }, 1500);
  }
}

function endGame() {
  state.gameOver = true;
  centerMessage.style.display = 'block';
  centerMessage.innerHTML = `Defeated on Round ${state.round}.<br/>Score: ${state.score}<br/><br/>Click to restart.`;
}

document.addEventListener('keydown', (e) => keys.add(e.code));
document.addEventListener('keyup', (e) => keys.delete(e.code));
document.addEventListener('mousedown', (e) => {
  if (e.button === 0) {
    mouseDown = true;
    if (document.pointerLockElement !== document.body) document.body.requestPointerLock();
    if (state.gameOver) restart();
    centerMessage.style.display = 'none';
  }
});
document.addEventListener('mouseup', () => (mouseDown = false));
document.addEventListener('mousemove', (e) => {
  if (document.pointerLockElement !== document.body) return;
  yaw -= e.movementX * 0.0022;
  pitch -= e.movementY * 0.0022;
  pitch = Math.max(-1.35, Math.min(1.25, pitch));
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const clock = new THREE.Clock();
spawnRound(1);

function animate() {
  const dt = Math.min(0.033, clock.getDelta());
  state.fireCooldown = Math.max(0, state.fireCooldown - dt);
  state.hitCooldown = Math.max(0, state.hitCooldown - dt);

  if (!state.gameOver) {
    const forward = new THREE.Vector3(Math.sin(yaw), 0, Math.cos(yaw));
    const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).negate();
    velocity.set(0, 0, 0);
    if (keys.has('KeyW')) velocity.add(forward);
    if (keys.has('KeyS')) velocity.sub(forward);
    if (keys.has('KeyD')) velocity.add(right);
    if (keys.has('KeyA')) velocity.sub(right);

    const sprint = keys.has('ShiftLeft') || keys.has('ShiftRight');
    const speed = sprint ? 11 : 7.2;
    if (velocity.lengthSq() > 0) velocity.normalize().multiplyScalar(speed * dt);
    camera.position.add(velocity);

    const radial = Math.hypot(camera.position.x, camera.position.z);
    if (radial > arenaRadius - 1.4) {
      const scale = (arenaRadius - 1.4) / radial;
      camera.position.x *= scale;
      camera.position.z *= scale;
    }

    state.bobTime += velocity.length() * 8;
    camera.position.y = 1.7 + Math.sin(state.bobTime) * (velocity.lengthSq() > 0 ? 0.04 : 0);
    camera.rotation.set(pitch, yaw, 0, 'YXZ');

    if (mouseDown) shoot();

    for (let i = bullets.length - 1; i >= 0; i--) {
      const b = bullets[i];
      b.mesh.position.addScaledVector(b.dir, b.speed * dt);
      b.ttl -= dt;
      let removed = b.ttl <= 0;

      if (!removed) {
        for (const enemy of enemies) {
          const hitDist = enemy.geometry.parameters.radius + 0.15;
          if (b.mesh.position.distanceTo(enemy.position) < hitDist) {
            enemy.userData.hp -= 14;
            enemy.userData.hitTimer = 0.12;
            removed = true;
            if (enemy.userData.hp <= 0) onEnemyKilled(enemy);
            break;
          }
        }
      }

      if (removed) {
        scene.remove(b.mesh);
        bullets.splice(i, 1);
      }
    }

    for (const enemy of enemies) {
      enemy.userData.hitTimer = Math.max(0, enemy.userData.hitTimer - dt);
      enemy.material.emissive.setHex(enemy.userData.hitTimer > 0 ? 0x883333 : 0x330909);

      const toPlayer = new THREE.Vector3().subVectors(camera.position, enemy.position);
      const dist = toPlayer.length();
      toPlayer.y = 0;
      if (dist > 1.7) {
        enemy.position.addScaledVector(toPlayer.normalize(), enemy.userData.speed * dt);
      } else if (state.hitCooldown <= 0) {
        state.hp -= enemy.userData.damage;
        state.hitCooldown = 0.42;
        hitFlash.style.opacity = '1';
        setTimeout(() => (hitFlash.style.opacity = '0'), 70);
        if (state.hp <= 0) endGame();
      }
      enemy.position.y = 0.9 + Math.sin(clock.elapsedTime * 3 + enemy.id) * 0.1;
    }

    ring.material.emissiveIntensity = 0.8 + Math.sin(clock.elapsedTime * 2) * 0.2;
  }

  updateHud();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

animate();
