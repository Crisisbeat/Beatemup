import wave
import struct
import math
import os
import random

def generate_wav(filename, duration_sec, freq_func, volume=0.5, sample_rate=44100, wave_type='sine'):
    """Genera un archivo .wav basado en una función de frecuencia."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    num_samples = int(duration_sec * sample_rate)
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        phi = 0
        for i in range(num_samples):
            t = i / sample_rate
            freq = freq_func(t)
            
            # Envelope (fade out)
            env = 1.0 - (i / num_samples)
            
            if wave_type == 'sine':
                value = math.sin(phi)
            elif wave_type == 'square':
                value = 1.0 if math.sin(phi) > 0 else -1.0
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            
            phi += 2 * math.pi * freq / sample_rate
            
            sample = int(value * volume * env * 32767)
            f.writeframesraw(struct.pack('<h', sample))

def create_sounds():
    print("Generando efectos de sonido...")
    
    # Player Hits (Impactos tipo 8-bit / Arcade)
    generate_wav('sounds/player_hit1.wav', 0.15, lambda t: 150 - t*400, volume=0.6, wave_type='square')
    generate_wav('sounds/player_hit2.wav', 0.18, lambda t: 180 - t*500, volume=0.6, wave_type='square')
    generate_wav('sounds/player_hit3.wav', 0.3, lambda t: 100 + math.sin(t*50)*50, volume=0.7, wave_type='square') # Finalizador potente
    
    # Damage (Sonidos de dolor/impacto recibido)
    generate_wav('sounds/player_damage.wav', 0.2, lambda t: 400 - t*1000, volume=0.5, wave_type='sine')
    generate_wav('sounds/enemy_damage.wav', 0.15, lambda t: 200 - t*500, volume=0.4, wave_type='noise') # Ruido para el enemigo
    generate_wav('sounds/enemy_hit.wav', 0.1, lambda t: 100, volume=0.5, wave_type='noise')
    
    # Power Up (Sonido ascendente)
    generate_wav('sounds/power_up.wav', 0.5, lambda t: 400 + t*1200, volume=0.4, wave_type='sine')
    
    # Bell for GO! (Sonido de campana metálica)
    generate_wav('sounds/go_bell.wav', 0.8, lambda t: 1200 - t*200, volume=0.5, wave_type='sine')
    
    # Stage 1 Music (Un loop simple de 4 segundos)
    print("Generando música de fondo (Stage 1)...")
    filename = 'sounds/music.wav'
    sample_rate = 44100
    duration = 4.0
    num_samples = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        notes = [261.63, 329.63, 392.00, 523.25] # C, E, G, C
        for i in range(num_samples):
            t = i / sample_rate
            note_idx = int(t * 4) % len(notes)
            freq = notes[note_idx]
            
            # Simple pulse synth
            value = 0.3 * (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)
            # Bass line
            value += 0.2 * math.sin(2 * math.pi * (freq/2) * t)
            
            sample = int(value * 32767)
            f.writeframesraw(struct.pack('<h', sample))

if __name__ == "__main__":
    create_sounds()
    print("¡Todos los sonidos han sido generados en la carpeta /sounds!")
