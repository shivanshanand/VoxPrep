"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";

function ParticleField() {
  const ref = useRef<THREE.Points>(null);
  
  // Generate random particles in a sphere
  const sphere = useMemo(() => {
    const particles = 3000;
    const positions = new Float32Array(particles * 3);
    for (let i = 0; i < particles; i++) {
      // Random position in a sphere
      // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/purity
      const r = 10 * Math.cbrt(Math.random());
      // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/purity
      const theta = Math.random() * 2 * Math.PI;
      // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/purity
      const phi = Math.acos(2 * Math.random() - 1);
      
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    return positions;
  }, []);

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 15;
      ref.current.rotation.y -= delta / 20;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#00f0ff"
          size={0.03}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={0.6}
        />
      </Points>
    </group>
  );
}

export function Scene() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 8], fov: 60 }}>
        <fog attach="fog" args={['#0a0e17', 2, 12]} />
        <ParticleField />
      </Canvas>
    </div>
  );
}
