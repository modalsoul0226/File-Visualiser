"""Assignment 2: Treemap Visualiser

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the code to run the treemap visualisation program.
It is responsible for initializing an instance of AbstractTree (using a
concrete subclass, of course), rendering it to the user using pygame,
and detecting user events like mouse clicks and key presses and responding
to them.
"""
import pygame
from tree_data import FileSystemTree
from population import PopulationTree


# Screen dimensions and coordinates
ORIGIN = (0, 0)
WIDTH = 1024
HEIGHT = 768
FONT_HEIGHT = 30                       # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree):
    """Display an interactive graphical display of the given tree's treemap.

    @type tree: AbstractTree
    @rtype: None
    """
    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, '')

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen, tree, text):
    """Render a treemap and text display to the given screen.

    Use the constants TREEMAP_HEIGHT and FONT_HEIGHT to divide the
    screen vertically into the treemap and text comments.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @type text: str
        The text to render.
    @rtype: None
    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))
    rect_lst = tree.generate_treemap((0, 0, WIDTH, TREEMAP_HEIGHT))
    # Draw the rectangles.
    for rect_i in rect_lst:
        pygame.draw.rect(screen, rect_i[1], rect_i[0])
    _render_text(screen, text)  # Display the text.
    # This must be called *after* all other pygame functions have run.
    pygame.display.flip()


def _render_text(screen, text):
    """Render text at the bottom of the display.

    @type screen: pygame.Surface
    @type text: str
    @rtype: None
    """
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen, tree):
    """Respond to events (mouse clicks, key presses) and update the display.

    Note that the event loop is an *infinite loop*: it continually waits for
    the next event, determines the event's type, and then updates the state
    of the visualisation or the tree itself, updating the display if necessary.
    This loop ends when the user closes the window.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @rtype: None
    """
    selected_leaf = None
    rect_dict = tree.rect_dict((0, 0, WIDTH, TREEMAP_HEIGHT))

    while True:
        # Wait for an event
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            return

        # When the user left-clicks on a file.
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Here, temp will be None if the screen is all black.
            temp = _get_selected(event.pos, rect_dict)
            # If nothing is selected i.e. the whole screen appears black or
            # the user clicks on the text box, nothing should happen.
            if not temp:
                pass
            # If it is the first click on the selected_leaf.
            elif temp != selected_leaf:
                selected_leaf = temp
                # Update the screen according to user's action.
                _display_helper(screen, tree, selected_leaf)
            # If user clicks on the selected leaf again, make the current
            # selected leaf unselected.
            else:
                render_display(screen, tree, '')
                selected_leaf = None

        # When the user right_clicks on a file
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            # Similarly, temp will be None if nothing is
            # displayed through screen.
            temp = _get_selected(event.pos, rect_dict)
            # Only operate when temp is not None i.e. a leaf is
            # selected. Here, I use pass because I want to simplify the
            # conditions of the following 'elif' statement.
            if not temp:
                pass
            # If selected_leaf is not the leaf currently deleted by user and
            # is not None, then the text rendered below will not be changed.
            elif selected_leaf and temp != selected_leaf:
                temp.del_leaf()
                # Update the rect_dict in order to sync the position of each
                # leaf.
                rect_dict = tree.rect_dict((0, 0, WIDTH, TREEMAP_HEIGHT))
                # Update the screen according to user's action. Here, text will
                # not change.
                _display_helper(screen, tree, selected_leaf)
            # If selected_leaf is already None or it is exactly the same leaf
            # user is trying to delete, then display no text and set the
            # selected_leaf to None.
            else:
                temp.del_leaf()
                selected_leaf = None
                rect_dict = tree.rect_dict((0, 0, WIDTH, TREEMAP_HEIGHT))
                render_display(screen, tree, '')

        # When user presses the up arrow or down arrow.
        # Only operate when a leaf is selected.
        elif event.type == pygame.KEYUP and selected_leaf:
            if event.key == pygame.K_UP:
                # Increase the size by one percent.
                selected_leaf.alt_size()
            elif event.key == pygame.K_DOWN:
                # Decrease the size by one percent.
                selected_leaf.alt_size(positive=False)
            # Update the rect_dict.
            rect_dict = tree.rect_dict((0, 0, WIDTH, TREEMAP_HEIGHT))
            # Update the screen.
            _display_helper(screen, tree, selected_leaf)


def _get_selected(pos, rect_dict):
    """This is a helper method used to return the AbstractTree that is selected
    by the user. Used by the treemap visualiser to keep track of the currently
    selected leaf.

    Return None if it is an empty tree or the total data size is zero i.e.
    when it displays nothing through visualiser.

    The parameter pos is always within the boundry of treemap visualiser's
    screen.
    If rect_dict is not empty, then pos is always in the dictionary. (Within
    the boundry of pygame rectangles contained in the dictionary.) Except the
    user clicks on the text box, return None in this case.

    @type pos: (int, int)
        This tuple represents the coordinate of the event induced by
        cursor's action.
    @type rect_dict: dict [tuple, AbstractTree]
        The key represents the pygame rectangle and the value represents
        the corresponding AbstractTree i.e. non-empty leaf.
    @rtype: AbstractTree | None
    """
    # If rect_dict is an empty dictionary, will skip the loop and return None.
    for rect in rect_dict:
        x, y, width, height = rect
        # If the pos of event is in the range of a rectangle, return the
        # corresponding AbstractTree.
        if x <= pos[0] <= x + width and y <= pos[1] <= y + height:
            return rect_dict[rect]


def _display_helper(screen, tree, selected_leaf):
    """Helper function for displaying or updating the change of tree according
    to user's action on the screen.

    Selected_leaf is not None.

    @type screen: Pygame.Surface
    @type tree: AbstractTree
    @type selected_leaf: AbstractTree
    """
    txt = selected_leaf.get_separator()
    prompt = '(' + str(selected_leaf.data_size) + ')'
    render_display(screen, tree, txt + prompt)


def run_treemap_file_system(path):
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.

    @type path: str
    @rtype: None
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


def run_treemap_population():
    """Run a treemap visualisation for World Bank population data.

    @rtype: None
    """
    pop_tree = PopulationTree(True)
    run_visualisation(pop_tree)


if __name__ == '__main__':
    import python_ta

    python_ta.check_errors(config='pylintrc.txt')
    python_ta.check_all(config='pylintrc.txt')

    run_treemap_file_system('F:\\SteamLibrary')
    # run_treemap_population()
