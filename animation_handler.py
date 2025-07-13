from animation import Animation
from random import shuffle

class AnimationHandler:
    def __init__(self):
        """Initialize the animation handler."""
        self.animations = []
        self.animations_to_remove = []
        
    def add_animation(self, animation):
        """
        Add an animation to the handler.
        
        Args:
            animation (Animation): The animation to add
        """
        if isinstance(animation, Animation):
            self.animations.append(animation)
        else:
            raise TypeError("animation must be an instance of Animation")
    
    def add_multiple_animations(self, animations: list[Animation],
                                spacing: int = 0, randomize: bool = False):
        """Adds multiple animations to the handler.
        The animations will start with different timings, depending on the spacing.
        If spacing is 0, all animations will start at once.
        If randomize is True, the start order will be randomized."""
        if randomize:
            shuffle(animations)
        
        for i, animation in enumerate(animations):
            animation.set_startup(i * spacing)
            self.add_animation(animation)

    def chain_animations(self, animation: Animation, chained_animations: list[Animation]):
        """
        Chain a list of animations to an existing animation.
        
        Args:
            animation (Animation): The animation to chain to
            chained_animations (list[Animation]): The animations to chain
        """
        animation.chained_animations = chained_animations
        self.add_animation(animation)
    
    def create_idle_animation(self, duration_frames=30, callback=None):
        """
        Create and add a basic idle animation that does nothing for several frames.
        
        Args:
            duration_frames (int): Number of frames to wait
            callback (callable): Optional function to call when animation completes
            
        Returns:
            Animation: The created animation
        """
        animation = Animation(duration_frames, callback)
        self.add_animation(animation)
        return animation
    
    def update(self):
        """
        Update all animations by one frame.
        
        Returns:
            bool: True if any animations are still running, False if all are complete
        """
        self.animations_to_remove.clear()
        
        for animation in self.animations:
            if not animation.update():
                # Animation completed, mark for removal
                self.animations_to_remove.append(animation)
        
        for animation in self.animations_to_remove:
            animation.end()
            for chained_animation in animation.chained_animations:
                self.add_animation(chained_animation)
            self.animations.remove(animation)
        
        return len(self.animations) > 0
    
    def has_animations(self):
        """
        Check if there are any animations currently running.
        
        Returns:
            bool: True if there are animations, False if none
        """
        return len(self.animations) > 0
    
    def clear_all(self):
        """Remove all animations."""
        self.animations.clear()
        self.animations_to_remove.clear()
    
    def get_animation_count(self):
        """Get the number of currently active animations."""
        return len(self.animations)
    
    def remove_animation(self, animation):
        """
        Remove a specific animation from the handler.
        
        Args:
            animation (Animation): The animation to remove
        """
        if animation in self.animations:
            self.animations.remove(animation)
    
    def get_animations(self):
        """Get a copy of the current animations list."""
        return self.animations.copy()