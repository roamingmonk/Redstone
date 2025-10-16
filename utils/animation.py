# utils/animation.py
import pygame
import time

class SpriteAnimation:
    """Professional sprite animation system - old school style"""
    
    def __init__(self, sprite_sheet_path, frame_count, frame_size, animation_speed=500):
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path)
            self.frame_count = frame_count
            self.frame_size = frame_size  # (width, height)
            self.animation_speed = animation_speed  # milliseconds
            self.current_frame = 0
            self.last_update = time.time() * 1000  # Convert to milliseconds
            
           # Extract individual frames with proper alpha handling
            self.frames = []
            for i in range(frame_count):
                frame_rect = pygame.Rect(i * frame_size[0], 0, frame_size[0], frame_size[1])
                
                # Extract the frame
                frame = self.sprite_sheet.subsurface(frame_rect)
                
                # Convert with alpha preservation
                if self.sprite_sheet.get_flags() & pygame.SRCALPHA:
                    frame = frame.convert_alpha()
                else:
                    frame = frame.convert()
                    
                self.frames.append(frame)
                
                # Debug: Check first frame
                if i == 0:
                    print(f"🔍 First frame size: {frame.get_size()}")
                    print(f"🔍 First frame has alpha: {frame.get_flags() & pygame.SRCALPHA}")
                    # Check a few pixels for transparency
                    for test_x in [0, 16, 31]:
                        for test_y in [0, 16, 31]:
                            pixel = frame.get_at((test_x, test_y))
                            #print(f"🔍 Pixel at ({test_x},{test_y}): {pixel}")
            
            print(f"✅ Animation loaded: {sprite_sheet_path} ({frame_count} frames)")
            
        except Exception as e:
            print(f"❌ Failed to load animation: {sprite_sheet_path} - {e}")
            # Create fallback frames
            self.frames = []
            for i in range(frame_count):
                fallback_frame = pygame.Surface(frame_size)
                fallback_frame.fill((255, 100, 0))  # Orange fallback
                self.frames.append(fallback_frame)
            self.frame_count = frame_count
            self.frame_size = frame_size
            self.animation_speed = animation_speed
            self.current_frame = 0
            self.last_update = time.time() * 1000
    
    def update(self):
        """Update animation frame based on timing"""
        current_time = time.time() * 1000
        if current_time - self.last_update > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_update = current_time
    
    def get_current_frame(self):
        """Get the current animation frame"""
        return self.frames[self.current_frame]
    
    def draw(self, surface, x, y):
        """Draw the current frame at specified position"""
        current_frame = self.get_current_frame()
        surface.blit(current_frame, (x, y))
    
    def reset(self):
        """Reset animation to first frame"""
        self.current_frame = 0
        self.last_update = time.time() * 1000