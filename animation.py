class Animation:
    def __init__(self, duration_frames=30, callback=None):
        """
        Initialize an animation.
        
        Args:
            duration_frames (int): Number of frames the animation should run
            callback (callable): Optional function to call when animation completes
        """
        self.duration_frames = duration_frames
        self.current_frame = 0
        self.callback = callback
        self.completed = False
        
    def update(self):
        """
        Update the animation by one frame.
        
        Returns:
            bool: True if animation is still running, False if completed
        """
        if self.completed:
            return False
            
        self.current_frame += 1
        
        # Perform the animation logic (override in subclasses)
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


class FadeAnimation(Animation):
    """Example animation that fades an object in/out."""
    
    def __init__(self, target_object, start_alpha=255, end_alpha=0, duration_frames=30, callback=None):
        """
        Initialize a fade animation.
        
        Args:
            target_object: Object with set_alpha method to fade
            start_alpha (int): Starting alpha value (0-255)
            end_alpha (int): Ending alpha value (0-255)
            duration_frames (int): Number of frames for the fade
            callback (callable): Optional function to call when animation completes
        """
        super().__init__(duration_frames, callback)
        self.target_object = target_object
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.alpha_range = end_alpha - start_alpha
        
        # Set initial alpha
        if hasattr(target_object, 'set_alpha'):
            target_object.set_alpha(start_alpha)
    
    def animate(self):
        """Update the fade effect."""
        if self.target_object and hasattr(self.target_object, 'set_alpha'):
            progress = self.get_progress()
            current_alpha = int(self.start_alpha + (self.alpha_range * progress))
            self.target_object.set_alpha(current_alpha)


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
        self.original_pos = None
        
        # Store original position
        if hasattr(target_object, 'x') and hasattr(target_object, 'y'):
            self.original_pos = (target_object.x, target_object.y)
    
    def animate(self):
        """Update the shake effect."""
        if self.target_object and self.original_pos:
            import random
            # Create random offset that decreases over time
            remaining_intensity = self.intensity * (1.0 - self.get_progress())
            offset_x = random.randint(-int(remaining_intensity), int(remaining_intensity))
            offset_y = random.randint(-int(remaining_intensity), int(remaining_intensity))
            
            if hasattr(self.target_object, 'x') and hasattr(self.target_object, 'y'):
                self.target_object.x = self.original_pos[0] + offset_x
                self.target_object.y = self.original_pos[1] + offset_y
    
    def reset(self):
        """Reset the shake animation and restore original position."""
        super().reset()
        if self.target_object and self.original_pos:
            if hasattr(self.target_object, 'x') and hasattr(self.target_object, 'y'):
                self.target_object.x = self.original_pos[0]
                self.target_object.y = self.original_pos[1]