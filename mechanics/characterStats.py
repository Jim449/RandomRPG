class CharacterStats:
    def __init__(self, stats: dict = None):
        self.stats = stats.copy() if stats else {}
    
    def set_stat(self, stat_name: str, value: int) -> None:
        """Set a stat value by name."""
        self.stats[stat_name] = value
    
    def get_stat(self, stat_name: str) -> int:
        """Get a stat value by name. Returns 0 if stat doesn't exist."""
        return self.stats.get(stat_name, 0)
    
    def modify_stat(self, stat_name: str, modifier: int) -> None:
        """Modify a stat value by adding the modifier."""
        current_value = self.get_stat(stat_name)
        self.set_stat(stat_name, current_value + modifier)
    
    def restore_stat(self, stat_name: str, max_stat: str, modifier: int) -> int:
        """Restore a stat value by adding the modifier, but not exceeding the max stat.
        Returns the amount of the stat restored."""
        current_value = self.get_stat(stat_name)
        max_value = self.get_stat(max_stat)
        if current_value >= max_value:
            return 0
        increase = min(modifier, max_value - current_value)
        value = current_value + increase
        self.set_stat(stat_name, value)
        return increase
    
    def deplete_stat(self, stat_name: str, modifier: int) -> int:
        """Deplete a stat value by subtracting the modifier.
        Stat will not go below 0. Returns the amount of the stat depleted."""
        current_value = self.get_stat(stat_name)
        if current_value <= 0:
            return 0
        decrease = min(modifier, current_value)
        value = current_value - decrease
        self.set_stat(stat_name, value)
        return decrease
        
    def remove_stat(self, stat_name: str) -> None:
        """Remove a stat from the character."""
        if stat_name in self.stats:
            del self.stats[stat_name]
    
    def get_all_stats(self) -> dict:
        """Get all stats as a dictionary."""
        return self.stats.copy()
    
    def clear_stats(self) -> None:
        """Remove all stats from the character."""
        self.stats.clear()

