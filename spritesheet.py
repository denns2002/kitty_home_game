import pygame


class Spritesheet:
    def __init__(self, filepath, sprite_size, spacing=(0, 0), scale=None) -> None:
        """Initialize the spritesheet.

        Args:
            filepath (Path): Path to the spritesheet image file.
            sprite_size (Tuple[int, int]): Width and height of each sprite in the sheet.
            spacing (Tuple[int, int], optional): Spacing between each sprite (row spacing, column spacing). Defaults to (0, 0).
            scale (Tuple[int, int], optional): Rescale each sprite to the given size. Defaults to None.
        """
        self._sheet = pygame.image.load(filepath).convert_alpha()
        self._sprite_size = sprite_size
        self._spacing = spacing
        self._scale = scale

    def get_sprite(self, loc, colorkey=None) -> pygame.Surface:
        """Load a specific sprite from the spritesheet.

        Args:
            loc (Tuple[int, int]): Location of the sprite in the sheet (row, column).
            colorkey (Union[pygame.Color, int, None], optional): Color to be treated as transparent. Defaults to None.

        Returns:
            pygame.Surface: The sprite image.
        """
        x = loc[1] * (self._sprite_size[0] + self._spacing[0])
        y = loc[0] * (self._sprite_size[1] + self._spacing[1])

        rect = pygame.Rect(x, y, *self._sprite_size)
        image = pygame.Surface(
            self._sprite_size, pygame.SRCALPHA
            ).convert_alpha()
        image.blit(self._sheet, (0, 0), rect)

        if colorkey:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        if self._scale:
            image = pygame.transform.scale(image, (image.get_width() * self._scale, image.get_height() * self._scale))

        return image

    def get_sprites(self, locs):
        """Load multiple sprites from the spritesheet.

        Args:
            locs (List[Tuple[int, int]]): List of locations of the sprites in the sheet (row, column).
            colorkey (Union[pygame.Color, int, None], optional): Color to be treated as transparent. Defaults to None.

        Returns:
            List[pygame.Surface]: List of sprite images.
        """
        return [self.get_sprite(loc) for loc in locs]
