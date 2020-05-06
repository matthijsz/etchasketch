This is a fun idea taken a bit too far. <br/>
# History
The idea was me and a friend would make an automated etch-a-sketch. So we quickly figured it would be an awesome idea if we could just feed a Raspberry Pi or whatever an image and it would automatically draw it for us. <br/>
This turned out to be harder then we initially thought, how do you go from an image, to some sort of path that you could draw on an etch-a-sketch? <br/>
Below is my solution. It uses a couple different search algorithms (A* and breadth-first search, depending on how far it has to travel). <br/>
# What it does
Running main.py will open a tkinter window where two options are available:<br/>
1. 'Get image from Google': This will require a Google Image Search API key to be placed in 'GoogleDeveloperKey.txt', and a Search engine ID to be placed in GoogleSearchEngineID.txt
2. 'Use an existing file': Open an image from your local storage<a/>
In the next window (or after you have entered your search query for Google) a preview of the monochrome image is presented (after all, an etch-a-sketch can only draw one color). Here the brightness cut-off for black pixels can be adjusted.<br/>
Finally a window is shown asking if an image should be saved at every step. This will generate a new folder in the directory of your image (or the directory you chose to store the image in the case of a Google search) called 'Steps', and it will save ech step as a separate image.<br/>
<br/>
The output will be a text file of instructions for whatever device, with each step on a new line, and comma seperated: `x-movement,y-movement` <br/>
where a positive value for x means move to the right, and a positive value for y means move down (negative means left and up respectively).<br/>

# Final remarks
We never got around to actually making the etch-a-sketch-robot, nevertheless I learned a lot coding this up. <br/>
If anyone out there wants to turn this into an etch-a-sketch feel free to use this code, and please show me the result! <br/>

# Output
Here is a sample of how this script would draw an image <br/>
![](output.gif)
