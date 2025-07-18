import pygame
from unit import Unit

class UserInterface():
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (36, 48, 36)
        self.health_color = (0, 0, 0)
        self.menu_color = (255, 255, 255)
        self.border_color = (24, 32, 24)
        self.outline_color = (255, 255, 255)
        self.overview_color = (255, 255, 255)
        self.enemy_info_color = (0, 0, 0)
        self.messages = []
        self.panel_width = 480
        self.panel_height = 128
        self.overview_height = 32
        self.menu_width = 96
        self.left_box_width = 192
        self.spell_width = 288
        self.right_width = 96
        self.message_width = 384
        self.panel_y = 480 - 128
        self.border_width = 3
        self.option_width = 96
        self.option_height = 26
        self.option_left_margin = 16
        self.option_top_margin = 16
        self.option_pointer_left_margin = 5
        self.health_x = 20
        self.magic_x = 400
        self.health_y = self.panel_y - 20
        self.menu_font = pygame.font.Font(None, 18)
        self.health_font = pygame.font.Font(None, 24)
        self.message_font = pygame.font.Font(None, 22)
        self.overview_font = pygame.font.Font(None, 20)
        self.target_pointer = pygame.image.load("resources/other/Pointer.png")
        self.target_pointer.convert_alpha()
        self.option_pointer = pygame.image.load("resources/other/Option_pointer_small.png")
        self.option_pointer.convert_alpha()

        self.main_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.main_panel.fill(self.border_color)
        pygame.draw.rect(self.main_panel, self.border_color, (0, 0, self.panel_width, self.panel_height), self.border_width)

        self.left_panel = pygame.Surface((self.menu_width, self.panel_height))
        self.left_panel.fill(self.background_color)
        pygame.draw.rect(self.left_panel, self.border_color, (0, 0, self.menu_width, self.panel_height), self.border_width)

        self.left_box = pygame.Surface((self.left_box_width, self.panel_height))
        self.left_box.fill(self.background_color)
        pygame.draw.rect(self.left_box, self.border_color, (0, 0, self.left_box_width, self.panel_height), self.border_width)

        self.spell_panel = pygame.Surface((self.spell_width, self.panel_height))
        self.spell_panel.fill(self.background_color)
        pygame.draw.rect(self.spell_panel, self.border_color, (0, 0, self.spell_width, self.panel_height), self.border_width)

        self.right_panel = pygame.Surface((self.right_width, self.panel_height))
        self.right_panel.fill(self.background_color)
        pygame.draw.rect(self.right_panel, self.border_color, (0, 0, self.right_width, self.panel_height), self.border_width)

        self.message_panel = pygame.Surface((self.message_width, self.panel_height))
        self.message_panel.fill(self.background_color)
        pygame.draw.rect(self.message_panel, self.border_color, (0, 0, self.message_width, self.panel_height), self.border_width)

        self.overview_panel = pygame.Surface((self.panel_width, self.overview_height))
        self.overview_panel.fill(self.background_color)
        pygame.draw.rect(self.overview_panel, self.border_color, (0, 0, self.panel_width, self.overview_height), self.border_width)

        self.full_message_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.full_message_panel.fill(self.background_color)
        pygame.draw.rect(self.full_message_panel, self.border_color, (0, 0, self.panel_width, self.panel_height), self.border_width)
    
    def draw_outline(self, text, x, y, font, color, outline_color,
                     negative_x: bool = False):
        outline = font.render(text, True, outline_color)
        surface = font.render(text, True, color)

        if negative_x:
            x = self.panel_width - x - surface.get_width()

        self.screen.blit(outline, (x - 1, y))
        self.screen.blit(outline, (x + 1, y))
        self.screen.blit(outline, (x, y - 1))
        self.screen.blit(outline, (x, y + 1))
        self.screen.blit(surface, (x, y))

    def draw_main_panel(self):
        self.screen.blit(self.main_panel, (0, self.panel_y))

    def draw_left_panel(self, options: list[str], y: int):
        self.screen.blit(self.left_panel, (0, self.panel_y))
        
        for i, option in enumerate(options):
            if i == y:
                self.screen.blit(self.option_pointer,
                                 (self.option_pointer_left_margin, self.panel_y + self.option_top_margin + (i * self.option_height)))
            text_surface = self.menu_font.render(option, True, self.menu_color)
            text_y = self.panel_y + self.option_top_margin + (i * self.option_height)
            self.screen.blit(text_surface, (self.option_left_margin, text_y))
    
    def draw_left_box(self, options: list[list[str]], x: int, y: int):
        self.screen.blit(self.left_box, (0, self.panel_y))

        for row in range(len(options)):
            text_y = self.panel_y + row * self.option_height + self.option_top_margin
            for col in range(len(options[row])):
                text_x = col * self.option_width + self.option_left_margin
                text_surface = self.menu_font.render(options[row][col], True, self.menu_color)
                self.screen.blit(text_surface, (text_x, text_y))

                if (col == x and row == y):
                    self.screen.blit(self.option_pointer,
                                     (text_x - self.option_left_margin + self.option_pointer_left_margin, text_y))

    def draw_spell_panel(self, options: list[list[str]], x: int, y: int):
        self.screen.blit(self.spell_panel, (self.menu_width, self.panel_y))

        for row in range(len(options)):
            text_y = self.panel_y + self.option_top_margin + (row * self.option_height)

            for col in range(len(options[row])):
                spell_name = str(options[row][col])
                text_x = self.menu_width + self.option_left_margin + (col * self.option_width)
                text_surface = self.menu_font.render(spell_name, True, self.menu_color)
                self.screen.blit(text_surface, (text_x, text_y))

                if (col == x and row == y):
                    self.screen.blit(self.option_pointer,
                                     (text_x - self.option_left_margin + self.option_pointer_left_margin, text_y))
                
    def draw_confirmation_panel(self, message: str, y: int):
        self.screen.blit(self.right_panel, (self.panel_width - self.right_width, self.panel_y))
        prompt_text = self.menu_font.render(message, True, self.menu_color)
        yes_text = self.menu_font.render("Yes", True, self.menu_color)
        no_text = self.menu_font.render("No", True, self.menu_color)
        prompt_x = self.panel_width - self.right_width + self.option_left_margin
        prompt_y = self.panel_y + self.option_top_margin
        self.screen.blit(prompt_text, (prompt_x, prompt_y))
        self.screen.blit(yes_text, (prompt_x, prompt_y + self.option_height))
        self.screen.blit(no_text, (prompt_x, prompt_y + self.option_height * 2))

        if y == 0:
            self.screen.blit(self.option_pointer,
                             (prompt_x - self.option_left_margin + self.option_pointer_left_margin, prompt_y + self.option_height))
        else:
            self.screen.blit(self.option_pointer,
                             (prompt_x - self.option_left_margin + self.option_pointer_left_margin, prompt_y + self.option_height * 2))

    def draw_info_panel(self, messages: list[str]):
        self.screen.blit(self.right_panel, (self.panel_width - self.right_width, self.panel_y))
        for row, message in enumerate(messages):
            text_surface = self.menu_font.render(message, True, self.menu_color)
            text_y = self.panel_y + self.option_top_margin + (row * self.option_height)
            self.screen.blit(text_surface, (self.option_left_margin, text_y))

    def draw_health_and_magic(self, player: Unit):
        health_text = self.health_font.render(
            f"HP {player.display_health} / {player.get_final_stat("MaxHealth")}",
            True, self.health_color)
        magic_text = self.health_font.render(
            f"MP {player.get_final_stat("Magic")} / {player.get_final_stat("MaxMagic")}",
            True, self.health_color)
        self.screen.blit(health_text, (self.health_x, self.health_y))
        self.screen.blit(magic_text, (self.magic_x, self.health_y))
    
    def draw_overview(self, player: Unit, area_name: str):
        self.screen.blit(self.overview_panel, (0, 0))
        health_text = self.overview_font.render(f"HP {player.get_final_stat("Health")} / {player.get_final_stat("MaxHealth")}",
                                                True, self.overview_color)
        magic_text = self.overview_font.render(f"MP {player.get_final_stat("Magic")} / {player.get_final_stat("MaxMagic")}",
                                               True, self.overview_color)
        area_text = self.overview_font.render(area_name, True, self.overview_color)
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(magic_text, (100, 10))
        self.screen.blit(area_text, (480 - 10 - area_text.get_width(), 10))

    def get_damage_coordinates(self) -> tuple[int, int]:
        return (self.health_x + 20, self.health_y - 10)
    
    def get_drain_coordinates(self) -> tuple[int, int]:
        return (self.magic_x + 20, self.health_y - 10)
    
    def draw_message_panel(self, panel: pygame.Surface):
        self.screen.blit(panel, (0, self.panel_y))

        for row, message in enumerate(self.messages):
            text_surface = self.message_font.render(message, True, self.menu_color)
            text_y = self.panel_y + self.option_top_margin + (row * self.option_height)
            self.screen.blit(text_surface, (self.option_left_margin, text_y))

    def set_message(self, message):
        self.messages = message.split("\n")
    
    def draw_pointer(self, combat_input):
        position = combat_input.get_target_pointer()
        enemy = combat_input.get_enemy()
        self.screen.blit(self.target_pointer, position)
        enemy_text = self.overview_font.render(f"{enemy.name} (lvl {enemy.level})",
                                               True, self.enemy_info_color)
        self.screen.blit(enemy_text, (240 - enemy_text.get_width() / 2, 10))
    
    def draw_mass_pointers(self, combat_input):
        for position in combat_input.get_mass_pointers():
            self.screen.blit(self.target_pointer, position)