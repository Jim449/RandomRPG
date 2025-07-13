import pygame

class UserInterface():
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (24, 32, 24)
        self.health_color = (0, 0, 0)
        self.menu_color = (238, 238, 238)
        self.border_color = (48, 64, 48)
        self.messages = []
        self.panel_width = 480
        self.panel_height = 128
        self.menu_width = 80
        self.spell_width = 320
        self.confirmation_width = 80
        self.message_width = 400
        self.panel_y = 480 - 128
        self.border_width = 2
        self.option_width = 112
        self.option_height = 26
        self.option_left_margin = 16
        self.option_top_margin = 16
        self.health_x = 20
        self.magic_x = 400
        self.health_y = self.panel_y - 20
        self.menu_font = pygame.font.Font(None, 16)
        self.health_font = pygame.font.Font(None, 24)
        self.message_font = pygame.font.Font(None, 22)
        self.pointer = pygame.image.load("resources/other/Option_pointer.png")

        self.main_panel = pygame.Surface((self.panel_width, self.panel_height))
        self.main_panel.fill(self.border_color)
        pygame.draw.rect(self.main_panel, self.border_color, (0, 0, self.panel_width, self.panel_height), self.border_width)

        self.menu_panel = pygame.Surface((self.menu_width, self.panel_height))
        self.menu_panel.fill(self.background_color)
        pygame.draw.rect(self.menu_panel, self.border_color, (0, 0, self.menu_width, self.panel_height), self.border_width)

        self.spell_panel = pygame.Surface((self.spell_width, self.panel_height))
        self.spell_panel.fill(self.background_color)
        pygame.draw.rect(self.spell_panel, self.border_color, (0, 0, self.spell_width, self.panel_height), self.border_width)

        self.confirmation_panel = pygame.Surface((self.confirmation_width, self.panel_height))
        self.confirmation_panel.fill(self.background_color)
        pygame.draw.rect(self.confirmation_panel, self.border_color, (0, 0, self.confirmation_width, self.panel_height), self.border_width)

        self.message_panel = pygame.Surface((self.message_width, self.panel_height))
        self.message_panel.fill(self.background_color)
        pygame.draw.rect(self.message_panel, self.border_color, (0, 0, self.message_width, self.panel_height), self.border_width)

    def draw_main_panel(self):
        self.screen.blit(self.main_panel, (0, self.panel_y))

    def draw_menu_panel(self, combat_input):
        self.screen.blit(self.menu_panel, (0, self.panel_y))
        
        for i, option in enumerate(combat_input.menu_options):
            if i == combat_input.menu_y:
                self.screen.blit(self.pointer, (0, self.panel_y + self.option_top_margin + (i * self.option_height)))
            text_surface = self.menu_font.render(option, True, self.menu_color)
            text_y = self.panel_y + self.option_top_margin + (i * self.option_height)
            self.screen.blit(text_surface, (self.option_left_margin, text_y))
    
    def draw_spell_panel(self, combat_input):
        self.screen.blit(self.spell_panel, (self.menu_width, self.panel_y))

        for row in range(4):
            for col in range(4):
                spell_name = combat_input.spell_options[row][col]
                text_x = self.menu_width + self.option_left_margin + (col * self.option_width)
                text_y = self.panel_y + self.option_top_margin + (row * self.option_height)
                if (col == combat_input.spell_x and row == combat_input.spell_y):
                    self.screen.blit(self.pointer, (text_x - self.option_left_margin, text_y))
                text_surface = self.menu_font.render(spell_name, True, self.menu_color)
                self.screen.blit(text_surface, (text_x, text_y))

    def draw_confirmation_panel(self, combat_input):
        self.screen.blit(self.confirmation_panel, (self.panel_width - self.confirmation_width, self.panel_y))
        prompt_text = self.menu_font.render(combat_input.confirmation_prompt, True, self.menu_color)
        yes_text = self.menu_font.render("Yes", True, self.menu_color)
        no_text = self.menu_font.render("No", True, self.menu_color)
        prompt_x = self.menu_width + self.spell_width + self.option_left_margin
        prompt_y = self.panel_y + self.option_top_margin
        self.screen.blit(prompt_text, (prompt_x, prompt_y))
        self.screen.blit(yes_text, (prompt_x, prompt_y + self.option_height))
        self.screen.blit(no_text, (prompt_x, prompt_y + self.option_height * 2))

        if combat_input.confirmation_y == 0:
            self.screen.blit(self.pointer, (prompt_x - self.option_left_margin, prompt_y + self.option_height))
        else:
            self.screen.blit(self.pointer, (prompt_x - self.option_left_margin, prompt_y + self.option_height * 2))

    def draw_health(self, player):
        health_text = self.health_font.render(
            f"HP {player.display_health} / {player.get_final_stat("MaxHealth")}",
            True, self.health_color)
        magic_text = self.health_font.render(
            f"MP {player.get_final_stat("Magic")} / {player.get_final_stat("MaxMagic")}",
            True, self.health_color)
        self.screen.blit(health_text, (self.health_x, self.health_y))
        self.screen.blit(magic_text, (self.magic_x, self.health_y))
    
    def get_damage_coordinates(self) -> tuple[int, int]:
        return (self.health_x, self.health_y - 10)
    
    def get_drain_coordinates(self) -> tuple[int, int]:
        return (self.magic_x, self.health_y - 10)
    
    def draw_message_panel(self):
        self.screen.blit(self.message_panel, (0, self.panel_y))

        for row, message in enumerate(self.messages):
            text_surface = self.message_font.render(message, True, self.menu_color)
            text_y = self.panel_y + self.option_top_margin + (row * self.option_height)
            self.screen.blit(text_surface, (self.option_left_margin, text_y))

    def set_message(self, message):
        self.messages = message.split("\n")