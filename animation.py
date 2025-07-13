from math import floor
import random

class Animation:
    def __init__(self, duration_frames=30, callback=None, startup=0):
        """
        Initialize an animation.
        
        Args:
            duration_frames (int): Number of frames the animation should run
            callback (callable): Optional function to call when animation completes
        """
        self.duration_frames = duration_frames
        self.current_frame = -startup
        self.callback = callback
        self.completed = False
        self.chained_animations: list[Animation] = []
        
    def update(self):
        """
        Update the animation by one frame.
        
        Returns:
            bool: True if animation is still running, False if completed
        """
        if self.completed:
            return False
            
        self.current_frame += 1
        
        if self.current_frame >= 0:
            self.animate()
        
        # Check if animation is complete
        if self.current_frame >= self.duration_frames:
            self.completed = True
            if self.callback:
                self.callback()
            return False
        
        return True
    
    def animate(self):
        """
        Override this method in subclasses to implement specific animation behavior.
        This base implementation does nothing (idle animation).
        """
        pass
    
    def is_completed(self):
        """Check if the animation has completed."""
        return self.completed
    
    def get_progress(self):
        """Get animation progress as a value between 0.0 and 1.0."""
        if self.duration_frames == 0:
            return 1.0
        return min(self.current_frame / self.duration_frames, 1.0)
    
    def reset(self):
        """Reset the animation to the beginning."""
        self.current_frame = 0
        self.completed = False

    def end(self):
        """Ends the animation. Override in subclasses."""
        pass

    def set_startup(self, startup: int):
        """Set the startup delay for the animation."""
        self.startup = startup
        self.current_frame = -startup
        

class FadeAnimation(Animation):
    """Example animation that fades an object in/out."""
    
    def __init__(self, target_object, start_alpha=255, end_alpha=0, speed=1, callback=None):
        """
        Initialize a fade animation.
        
        Args:
            target_object: Object with set_alpha method to fade
            start_alpha (int): Starting alpha value (0-255)
            end_alpha (int): Ending alpha value (0-255)
            duration_frames (int): Number of frames for the fade
            callback (callable): Optional function to call when animation completes
        """
        super().__init__(0, callback)
        self.target_object = target_object
        self.current_alpha = start_alpha
        self.end_alpha = end_alpha
        self.alpha_range = abs(start_alpha - end_alpha)
        self.direction = 1 if start_alpha < end_alpha else -1
        self.speed = speed
        self.duration_frames = floor(self.alpha_range / self.speed)
        self.target_object.set_alpha(start_alpha)
    
    def animate(self):
        """Update the fade effect."""
        self.current_alpha += self.speed * self.direction
        self.target_object.set_alpha(self.current_alpha)

    def end(self):
        """End the fade animation."""
        self.target_object.set_alpha(self.end_alpha)


class ShakeAnimation(Animation):
    """Example animation that shakes an object."""
    
    def __init__(self, target_object, intensity=5, duration_frames=15, callback=None):
        """
        Initialize a shake animation.
        
        Args:
            target_object: Object with original position to shake
            intensity (int): How far to shake the object
            duration_frames (int): Number of frames for the shake
            callback (callable): Optional function to call when animation completes
        """
        super().__init__(duration_frames, callback)
        self.target_object = target_object
        self.intensity = intensity
        self.original_pos = (target_object.x, target_object.y)
    
    def animate(self):
        """Update the shake effect."""
        remaining_intensity = self.intensity * (1.0 - self.get_progress())
        offset_x = random.randint(-int(remaining_intensity), int(remaining_intensity))
        offset_y = random.randint(-int(remaining_intensity), int(remaining_intensity))
        self.target_object.x = self.original_pos[0] + offset_x
        self.target_object.y = self.original_pos[1] + offset_y
    
    def reset(self):
        """Reset the shake animation and restore original position."""
        super().reset()
        self.target_object.x = self.original_pos[0]
        self.target_object.y = self.original_pos[1]
    
    def end(self):
        self.target_object.x = self.original_pos[0]
        self.target_object.y = self.original_pos[1]


class TextAscendAnimation(Animation):
    def __init__(self, screen, x, y, message, font, color=(255, 255, 255), speed=1, fadeout=1, callback=None):
        super().__init__(0, callback)
        self.screen = screen
        self.x = x
        self.y = y
        self.message = message
        self.font = font
        self.color = color
        self.speed = speed
        self.duration_frames = floor(255 / fadeout)
        self.fadeout = fadeout
        self.alpha = 255
        self.text = self.font.render(self.message, True, self.color)

    def animate(self):
        self.y -= self.speed
        self.alpha -= self.fadeout
        self.text.set_alpha(self.alpha)
        self.screen.blit(self.text, (self.x, self.y))

    def end(self):
        self.text.set_alpha(0)


class TextWriteAnimation(Animation):
    def __init__(self, target_object, message, font, speed=1, delay=30, callback=None):
        super().__init__(0, callback)
        self.target_object = target_object
        self.full_message = message
        self.current_message = ""
        self.font = font
        self.speed = speed
        self.duration_frames = floor(len(message) / speed) + delay
        self.delay = delay
    
    def animate(self):
        if self.current_message != self.full_message:
            first_letter = (self.current_frame - 1) * self.speed
            last_letter = min(self.current_frame * self.speed, len(self.full_message))
            self.current_message += self.full_message[first_letter:last_letter]
            self.target_object.set_message(self.current_message)


class WalkDownAnimation(Animation):
    def __init__(self, target_object, speed=4, distance=16, callback=None):
        super().__init__(0, callback)
        self.duration_frames = floor(distance / speed)
        self.target_object = target_object
        self.speed = speed
        self.distance = distance
        self.original_pos = None  # Will be set when animation starts
    
    def animate(self):
        # Capture original position on first frame
        if self.original_pos is None:
            self.original_pos = (self.target_object.x, self.target_object.y)
        
        self.target_object.y += self.speed
    
    def end(self):
        if self.original_pos is not None:
            self.target_object.y = self.original_pos[1] + self.distance


class WalkUpAnimation(Animation):
    def __init__(self, target_object, speed=4, distance=16, callback=None):
        super().__init__(0, callback)
        self.duration_frames = floor(distance / speed)
        self.target_object = target_object
        self.speed = speed
        self.distance = distance
        self.original_pos = None  # Will be set when animation starts
    
    def animate(self):
        # Capture original position on first frame
        if self.original_pos is None:
            self.original_pos = (self.target_object.x, self.target_object.y)
        
        self.target_object.y -= self.speed
    
    def end(self):
        if self.original_pos is not None:
            self.target_object.y = self.original_pos[1] - self.distance


class BlinkAnimation(Animation):
    def __init__(self, target_object, interval=1, duration_frames=30, callback=None):
        super().__init__(duration_frames, callback)
        self.target_object = target_object
        self.interval = interval
        
    def animate(self):
        if self.current_frame % (self.interval * 2) < self.interval:
            self.target_object.flashing = True
        else:
            self.target_object.flashing = False
    
    def end(self):
        self.target_object.flashing = False


class RelativeMovementAnimation(Animation):
    def __init__(self, target_object, dx=0, dy=0, speed=2, callback=None):
        """
        Move an object relative to its current position.
        
        Args:
            target_object: Object to move
            dx (int): Distance to move in x direction (can be negative)
            dy (int): Distance to move in y direction (can be negative)
            speed (int): Speed of movement per frame
            callback (callable): Optional callback when animation completes
        """
        total_distance = max(abs(dx), abs(dy))
        super().__init__(floor(total_distance / speed), callback)
        self.target_object = target_object
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.step_x = (dx / total_distance) * speed if total_distance > 0 else 0
        self.step_y = (dy / total_distance) * speed if total_distance > 0 else 0
        self.start_pos = None
        self.target_pos = None
    
    def animate(self):
        # Capture positions on first frame
        if self.start_pos is None:
            self.start_pos = (self.target_object.x, self.target_object.y)
            self.target_pos = (self.start_pos[0] + self.dx, self.start_pos[1] + self.dy)
        
        self.target_object.x += self.step_x
        self.target_object.y += self.step_y
    
    def end(self):
        if self.target_pos is not None:
            self.target_object.x = self.target_pos[0]
            self.target_object.y = self.target_pos[1]