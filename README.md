# File-Visualiser
 This is a visualisation that shows a tree's structure according to the weights (or sizes) of its data values, using nested rectangle to show subtrees, scaled to different dimensions to reflect the proportional sizes of each piece of data. Treemaps are used in many contexts. Among the more popular uses are news headlines, various kinds of financial information, and computer disk usage.

## Visualiser: displaying the treemap
The code in treemap_visualiser.py runs the treemap algorithm, and then uses pygame directly to render a graphical display to the user.
The pygame window is divided into two parts:
* The treemap itself (a collection of colourful rectangles).
* A text display along the bottom of the window, showing information about the currently selected rectangle, or nothing, if no rectangle is selected.


![picture](/pygame_treemap.png)
Every rectangle corresponds to one leaf (not of data_size zero) in the tree. If the whole tree has data_size zero (so no rectangles are returned by treemap), the entire screen should appear black.

## Visualiser: user events
In addition to displaying the treemap, the pygame graphical display responds to a few different **events**:

a. The user can close the window by clicking the X icon (like any other window)

b. The user can **left-click on a rectangle** to select it. The text display updates to show two things:
  * the names of the nodes on the path from the root to the selected leaf, separated by a subclass-specific separator string
  * the selected leaf's data_size

The user can change their selection simply by clicking on a different rectangle. If the user clicks again on the currently-selected rectangle, that rectangle becomes unselected (and so no rectangles are selected, and no text is shown).

The following two events allow the user to actually mutate the tree, which shows how to turn a static visualisation into a tool for simulating changes on a dataset, and seeing what would happen. Once the user performs one of these events, the tree is no longer in sync with the original data set, and instead represents hypothetical sizes based on the user's actions.

All changes described below **only change the tree object**; so if a rectangle is deleted or its size changes, **WILL NOT** change the actual file on your computer!

c. If the user **right-clicks** on a rectangle, the corresponding leaf is **deleted** from the tree. This leaf's ancestors must all have their data_size attributes updated, and the visualisation updates to show the new sizes.

Details:

* Even if the user deletes all the children of a node, it should still remain in the tree. However, that node's data_size will become 0, and so it will disappear from the visualisation.
* If the user deletes the currently-selected rectangle, after the deletion no rectangle is selected, and no text is shown.

d. If the user presses the Up Arrow or Down Arrow key when a rectangle is selected, the selected leaf's data_size increases or decreases by 1% of its current value, respectively. This affects the data_size of its ancestors as well, and the visualisation must update to show the new sizes.

Details:

* A leaf's data_size cannot decrease below 1. There is no upper limit on the value of data_size.
* The 1% amount is always rounded up before applying the change. For example, if a leaf's data_size value is 150, then 1% of this is 1.5, which is rounded up to 2. So its value could increase up to 152, or decrease down to 148.

Inspired by the following softwares:
* [WinDirStat    (Windows)](https://portableapps.com/apps/utilities/windirstat_portable)
* [Disk Inventory X (OS X)](http://www.derlien.com/)
* [KDirStat (Linux)](http://kdirstat.sourceforge.net/)
