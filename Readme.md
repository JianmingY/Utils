### put the script in a ROOT directory, one above the participant folders(eg. in expert/ or in novice/)

### For the QtAnnotator
Creator: Jianming Yang

Preparation: 
1. Make a labe name file: each line is a label class, load firstly
2. Prepare images that needs to be label in a folder, load secondly

Key uses:
0. Default first class (Key_1), number key to change class
1. Left Click and drag to draw box
2. Right click and drag to move box
3. Key_V to copy previous image's label to the current one
4. Key_C to clear all boxes on current image
5. Key_Backspace to delete the box where the cursor is pointing
6. Key_A to start adjusting the box where the cursor is pointing:
   - left click on the squares to modify the box
8. Key_D go to the next image
9. Key_S go to the previsous one

Colors: (besides the box colors)
1. cyan - you are drawing a new box
2. red - you are dragging a box
3. yellow - you are adjusting a box

To Do:  1. When the text is outside the image, it auto fits to the view - shrinking image & deforming boxes ------------- sol: print where it's in the image
        2. Make the class panel clickagble to account for # of classes greater than 10
        3. Add go back function
        4. Clean up code to make it look nicer
