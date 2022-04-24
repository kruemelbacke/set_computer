"""
blblblblbl
"""
import pygame


class GUI():
    def __init__(self):
        """
        Inits GUI
        """
        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("SET! Game")

        self.clock = pygame.time.Clock()

        self.color = (255,255,255)

        self.color_light = (170,170,170)

        self.color_dark = (100,100,100)

        self.width = self.screen.get_width()

        self.height = self.screen.get_height()

        self.smallfont = pygame.font.SysFont('Corbel',35)

        self.text = self.smallfont.render('Quit' , True , self.color)

        self.game_active = True

    def run(self):
        """
        Run GUI
        """

        while self.game_active:

            for ev in pygame.event.get():
                self.mouse = pygame.mouse.get_pos()

                if ev.type == pygame.QUIT:
                    self.game_active = False

                if ev.type == pygame.MOUSEBUTTONDOWN:

                    if (self.width/2 <= self.mouse[0] <= self.width/2+140
                        and self.height/2 <= self.mouse[1] <= self.height/2+40):
                        self.game_active = False

            self.screen.fill((60,25,60))

            # check if mouse is on button
            if (self.width/2 <= self.mouse[0] <= self.width/2+140
                and self.height/2 <= self.mouse[1] <= self.height/2+40):
                pygame.draw.rect(self.screen,self.color_light,[self.width/2,self.height/2,140,40])

            else:
                pygame.draw.rect(self.screen,self.color_dark,[self.width/2,self.height/2,140,40]) 

            self.screen.blit(self.text , (self.width/2+50,self.height/2))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    myGUI = GUI()
    myGUI.run()
