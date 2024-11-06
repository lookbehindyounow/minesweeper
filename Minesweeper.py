from tkinter import Tk,Frame,Label,Entry,Button,PhotoImage,Canvas,Scrollbar # GUI library
import tkinter.font as Font
from random import randint # placing mines
from time import time # timer

window=Tk() # window
window.geometry(f"900x720+{window.winfo_screenwidth()//2-360}+{window.winfo_screenheight()//2-360}")
window.frame=Frame(window)
window.frame.pack()

explosion_pic=PhotoImage(master=window,file="explosion.png") # loading images
flag_pic=PhotoImage(master=window,file="flag.png")
mine_pic=PhotoImage(master=window,file="mine.png")
flagged_mine_pic=PhotoImage(master=window,file="flagged_mine.png")

colours=["blue","green","red","magenta","maroon","#0db879","grey","black"]

# ---------------------------------------------------------------------------------------------------------------- #
#                                                     Pre-game                                                     #
# ---------------------------------------------------------------------------------------------------------------- #

def menu(): # displays menu
    [widget.destroy() for widget in window.frame.winfo_children()] # get rid of whatever was in canvas before putting something new in
    if (window.winfo_width(),window.winfo_height())!=(900,720):
        window.geometry("900x720") # resizing if necessary
    Label(window.frame).grid() # spacer
    inputs=[None]*4
    for i,key in zip(range(4),state): # these are the text fields for the menu (name,rows,columns,mines)
        Label(window.frame,text=key).grid()
        inputs[i]=Entry(window.frame)
        inputs[i].insert(0,state[key])
        inputs[i].grid(row=i+1,column=1)
    Label(window.frame).grid() # spacer
    Button(window.frame,text="Start",command=lambda:setup(inputs)).grid()
    Button(window.frame,text="Leaderboards",command=present).grid(row=6,column=1)

def setup(inputs): # validates input & sets up button grid
    # validates input
    message=None
    maximums=[None,(window.winfo_screenheight()-150)//21,(window.winfo_screenwidth()-40)//20,None] # TODO: recalculate maximums
    for i,key in zip(range(4),state):
        state[key]=inputs[i].get()
        if i==0: # for name input
            if len(state["name"])>40:
                message="name must be less than 40 characters"
                break
            continue # skip numerical validation for name
        if not state[key].isdigit():
            message=key+" must be an integer"
            break
        state[key]=int(state[key])
        if state[key]==0 or state[key]>maximums[i]:
            message=f"{key} must be between 1 & {maximums[i]}"
            break
        if i==2:
            maximums[3]=state["rows"]*state["columns"]-1 # can only safely calculate maximum mines after validating rows & columns

    [widget.destroy() for widget in window.frame.winfo_children()] # clear menu before showing input validation message or setting up grid

    if message: # show input validation message
        Label(window.frame).grid() # spacer
        Label(window.frame,text=message).grid()
        Label(window.frame).grid() # spacer
        Button(window.frame,text="Okay",command=menu).grid()
        return

    state["first click"]=True # mines are placed & timer starts on first click
    state["game over"]=False # game mechanic functions won't work when game over

    if state["rows"]>31 or state["columns"]>34: # resizes window if necessary TODO: recalculate when resizing is required
        screen_height=max(21*state["rows"]+90,720) # TODO: recalculate how much resizing is required
        screen_width=max(20*state["columns"]+40,720)
        window.geometry(f"{screen_width}x{screen_height}")

    # creates & displays button grid & binds functions to button mouse events
    Label(window.frame).grid() # spacer
    minefield=Frame(window.frame,bg="#777")
    minefield.grid()
    state["buttons"]=[[Label(minefield,text="",bg="#aaa",bd=0,highlightthickness=0) for c in range(state["columns"])] for r in range(state["rows"])]
    for row in range(state["rows"]):
        pad_y=(int(row==0),1)
        for column in range(state["columns"]):
            pad_x=(int(column==0),1)
            state["buttons"][row][column].grid(row=row,column=column,padx=pad_x,pady=pad_y,ipadx=0,ipady=0,sticky="nsew")
            state["buttons"][row][column].bind("<Button-1>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<Button-3>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<ButtonRelease-1>",lambda event,row=row,column=column:reveal(event,row,column))
            state["buttons"][row][column].bind("<ButtonRelease-3>",lambda event,row=row,column=column:flag(row,column))
    size=Font.nametofont("TkDefaultFont").metrics("linespace")+3
    [minefield.rowconfigure(row,minsize=size) for row in range(state["rows"])]
    [minefield.columnconfigure(column,minsize=size) for column in range(state["columns"])]
    Label(window.frame).grid() # spacer
    Button(window.frame,text="Reset",command=menu).grid()
    state["time label"]=Label(window.frame)
    state["time label"].grid()

# ---------------------------------------------------------------------------------------------------------------- #
#                                             Game Mechanic Functions                                              #
# ---------------------------------------------------------------------------------------------------------------- #

def start(row,column): # decides placement of mines & starts timer
    state["first click"]=False
    # U=unclicked empty space
    # M=unclicked mine
    # [empty string]=empty space with no adjacent mines
    # [number n from 1-8]=empty space with n adjacent mines
    # FM=correctly flagged mine
    # FF=incorrectly flagged empty space
    state["grid"]=[["U" for c in range(state["columns"])] for r in range(state["rows"])] # <-- creates empty grid
    mine_counter=state["mines"]
    while mine_counter>0:
        random_row=randint(0,state["rows"]-1)
        random_column=randint(0,state["columns"]-1)
        if state["grid"][random_row][random_column]=="U" and (random_row,random_column)!=(row,column):
            state["grid"][random_row][random_column]="M"
            mine_counter-=1
    state["start time"]=time()
    update_timer()

def update_timer(): # updates timer every second, synchronises clock with real time & schedules next update
    if state["game over"]: return
    state["time label"].config(text=str(round(time()-state["start time"],0))[0:-2]+"s") # update
    wait=1000*round((state["start time"]-time())%1,3) # synch
    window.after(int(wait),update_timer) # schedule

def clicked(row,column): # buttons go down when you click them but don't reveal/flag until you let go
    if state["game over"]: return
    # first click is in condition because state["grid"] doesn't exist yet on first click
    if state["first click"] or state["grid"][row][column] in ["U","M","FF","FM"]:
        state["buttons"][row][column].config(bg="#888")

def reveal(event,row,column): # reveals if clicked square is mine or empty
    if event.state&12: # ctrl/cmd+click to flag
        flag(row,column)
        return
    if state["game over"]: return
    if state["first click"]: start(row,column)
    if state["grid"][row][column]=="U": # if there's no mine to to the revealing algorithm
        reveal_more(row,column)
        check()
    elif state["grid"][row][column]=="M": # if there's a mine game over
        state["buttons"][row][column].config(image=explosion_pic,bg="#ccc")
        state["grid"][row][column]="*" # so it doesn't get shown as an unexploded mine in the game over mine reveal
        end(True)
    elif state["grid"][row][column] in ["FF","FM"]:
        state["buttons"][row][column].config(bg="#aaa")

def reveal_more(row,column): # reveals number of adjacent mines & if it's 0, does the same for all empty adjacent squares
    to_do=[(row,column)] # stack of squares to be revealed
    while to_do:
        location=to_do.pop()
        adjacent_mines=0
        new_places=0
        for vertical in range(3): # each iteration scans a row in the surrounding 3x3 square
            if(location[0]==0 and vertical==0) or (location[0]==state["rows"]-1 and vertical==2):
                continue # ^skip 1st row scan if we're at the top or last row scan if we're at the bottom
            for horizontal in range(3):
                if(location[1]==0 and horizontal==0) or (location[1]==state["columns"]-1 and horizontal==2) or (vertical,horizontal)==(1,1):
                    continue # ^skip 1st column scan if we're at the left side or last column scan if we're at the right side, also skip scanning the square we're on
                adjacent_square=state["grid"][location[0]+vertical-1][location[1]+horizontal-1]
                adjacent_square_coords=(location[0]+vertical-1,location[1]+horizontal-1)
                if adjacent_square in ["M","FM"]: # if adjacent square is a mine, increment adjacent mines
                    adjacent_mines+=1
                elif adjacent_mines==0 and (adjacent_square_coords not in to_do) and adjacent_square=="U":
                    # if no adjacent mines (yet) & an adjacent square is unclicked & not already on the to do list
                    to_do.append((location[0]+vertical-1,location[1]+horizontal-1)) # put it in the to do list
                    new_places+=1 # count how many squares added to to_do incase they need removed
        if adjacent_mines>0: # if square is numbered & not blank
            if new_places: del to_do[-new_places:] # don't reveal adjacent squares by removing from to_do
            state["grid"][location[0]][location[1]]=str(adjacent_mines) # update grid
            state["buttons"][location[0]][location[1]].config(text=state["grid"][location[0]][location[1]],
                fg=colours[adjacent_mines-1],bg="#ccc",font=("Helvetica",9,"bold"),image="")
        else:
            state["grid"][location[0]][location[1]]="" # update grid
            state["buttons"][location[0]][location[1]].config(bg="#ccc")

def flag(row,column): # puts a flag when you right click
    if state["game over"]: return
    if state["first click"]: start(row,column)
    if state["grid"][row][column]=="M":
        state["grid"][row][column]="FM"
        state["buttons"][row][column].config(image=flag_pic,bg="#aaa")
    elif state["grid"][row][column]=="U":
        state["grid"][row][column]="FF"
        state["buttons"][row][column].config(image=flag_pic,bg="#aaa")
    elif state["grid"][row][column]=="FM":
        state["grid"][row][column]="M"
        state["buttons"][row][column].config(image="",bg="#aaa")
    elif state["grid"][row][column]=="FF":
        state["grid"][row][column]="U"
        state["buttons"][row][column].config(image="",bg="#aaa")
    check()

def check(): # checks if the game is won
    empty_squares_unclicked=False # there are 2 ways to win, reveal all empty spaces or correctly flag all mines
    flags_incomplete=False
    for row in state["grid"]:
        for column in row:
            if column in["FF","U"]: # any incorrect flags or unclicked squares
                empty_squares_unclicked=True
            if column in["FF","M"]: # any incorrect flags or unflagged mines
                flags_incomplete=True
            if empty_squares_unclicked and flags_incomplete: # leave the check when both winning conditions are failed to save time
                return
    end(False)

# ---------------------------------------------------------------------------------------------------------------- #
#                                                    Game Over                                                     #
# ---------------------------------------------------------------------------------------------------------------- #

def end(lost): # stops timer, reveals mines, adds time to leaderboards
    state["time taken"]=round(time()-state["start time"],3) # stop timer
    state["game over"]=True
    # reveal mines
    [[state["buttons"][r][c].config(image=mine_pic if state["grid"][r][c]=="M" else (flagged_mine_pic if state["grid"][r][c]=="FM" else None)) for c in range(state["columns"])] for r in range(state["rows"])]
    if lost: return # nothing more to do if player lost
    state["time label"].config(text=(f"Player time: {state["time taken"]}s")) # shows your time
    # TODO: add a button to add your score to leaderboard optionally
    leaderboards=access() # get leaderboards from file
    if leaderboards==[]: # if file not found, corrupt or empty
        file=open("leaderboards.txt","w")
        file.write(f"{state["rows"]},{state["columns"]},{state["mines"]}|{state["name"]}:{state["time taken"]}\n")
        file.close()
        return
    player_category=(state["rows"],state["columns"],state["mines"])
    player_score=(state["name"],state["time taken"])
    player_category_rank=[state["rows"]*state["columns"],state["mines"]] # categories are ranked by grid size then mine count
    for i,[(rows,columns,mines),scores] in enumerate(leaderboards): # for each category
        category_rank=[rows*columns,mines]
        if player_category_rank[0]<category_rank[0]: continue # if grid size smaller than this category, skip to next category
        if player_category_rank[0]>category_rank[0]: # if grid size bigger than this category, insert new category here & break
            leaderboards.insert(i,[player_category,[player_score]])
            break
        elif player_category_rank[0]==category_rank[0]: # grid size equal to this category
            if player_category_rank[1]<category_rank[1]: continue # if mine count less than this category, skip to next category
            if player_category_rank[1]>category_rank[1]: # if mine count more than this category, insert new category here & break
                leaderboards.insert(i,[player_category,[player_score]])
                break
            elif player_category_rank[1]==category_rank[1]: # grid size & mine count equal to this category # TODO: this does not mean categories are the same grid shape, add new category if rows different
                # get first index where player time faster than this time or get len(scores) if player time is slowest
                player_rank=next((j for j,score in enumerate(scores) if player_score[1]<score[1]),len(scores))
                leaderboards[i][1].insert(player_rank,player_score) # insert score here & break
                break
    file_string=""
    for [rows,columns,mines],score in leaderboards: # formats leaderboards to string for txt file
        file_string+=f"{rows},{columns},{mines}|"
        for name,time_taken in score:
            file_string+=f"{name}:{time_taken},"
        file_string=file_string[:-1]+"\n"
    file=open("leaderboards.txt","w")
    file.truncate()
    file.write(file_string)
    file.close()

# ---------------------------------------------------------------------------------------------------------------- #
#                                                   Leaderboards
# ---------------------------------------------------------------------------------------------------------------- #

def mouse_scroll(event,boardframe): # this is the event called by the mouse scrollwheel & where it links to the scrollable bit
    boardframe.yview_scroll(-int(event.delta/120),"units")

def present(): # shows the leaderboards
    [widget.destroy() for widget in window.frame.winfo_children()]
    Label(window.frame).grid() # spacer
    leaderboards=access() # get the leaderboards table from file
    if leaderboards:
        Label(window.frame,text="Player",relief="ridge",width=64).grid()
        Label(window.frame,text="Time",relief="ridge",width=15).grid(row=1,column=1)
        Label(window.frame).grid() # spacer

        boardframe=Canvas(window.frame,yscrollincrement="2") # this is the object that is scrollable
        boardframe.bind_all("<MouseWheel>",lambda event:mouse_scroll(event,boardframe)) # this is what calls the event when the mouse wheel scrolls
        boardframe.grid(columnspan=2)
        scrollbar=Scrollbar(window.frame,command=boardframe.yview) # this is the scrollbar you can click & drag
        scrollbar.grid(row=3,column=2,sticky="ns")
        boardframe.config(yscrollcommand=scrollbar.set)
        
        board=Frame(boardframe) # this is where the actual tables are put on screen
        line=0
        for mode in leaderboards: # for every category
            Label(board,text=str(mode[0][0])+"x"+str(mode[0][1])+" grid, "+str(mode[0][2])+" mines").grid(row=line,column=0,columnspan=2)
            line+=1
            for entry in mode[1]: # for every time
                Label(board,text=entry[0],relief="ridge",width=64).grid(row=line,column=0) # TODO: recalculate widths
                written_time=str(round(entry[1]%60,4))+"s" # this bit figures out if it goes into minutes or hours
                if entry[1]>=60:
                    written_time=str(int(entry[1]%3600//60))+"m "+written_time
                    if entry[1]>=3600:
                        written_time=str(int(entry[1]//3600))+"h "+written_time
                Label(board,text=written_time,relief="ridge",width=15).grid(row=line,column=1)
                line+=1
            if leaderboards.index(mode)!=len(leaderboards)-1:
                Label(board).grid() # spacer label for gaps between each board
                line+=1
        
        boardframe.create_window((0,0),window=board,anchor="nw") # this is all more scrollbar stuff
        board.update_idletasks() # keeps the scrollbar updating
        boardframe.config(width=board.winfo_width(),height=min(line*21,538))
        boardframe.config(scrollregion=boardframe.bbox("all"))
        
        Label(window.frame).grid() # spacer
        Button(window.frame,text="Clear leaderboards",command=empty_leaderboards,width=15).grid()
        Label(window.frame).grid() # spacer
    else: # if the leaderboards are empty
        Label(window.frame,text="There are no leaderboard entries yet.").grid()
        Label(window.frame).grid() # spacer
    Button(window.frame,text="Back",command=menu).grid(row=5,column=1)

def present_no_gui():
    leaderboards=access()
    print("leaderboards:")
    for mode in leaderboards:
        print(f"    {mode[0][0]}x{mode[0][1]} grid with {mode[0][2]} mines:")
        for entry in mode[1]:
            written_time=str(round(entry[1]%60,4))+"s" # this bit figures out if it goes into minutes or hours
            if entry[1]>=60:
                written_time=str(int(entry[1]%3600//60))+"m "+written_time
                if entry[1]>=3600:
                    written_time=str(int(entry[1]//3600))+"h "+written_time
            print(f"        {entry[0]}: {written_time}")
        print()

def access(): # reads the file & formats into [[rows,columns,mines],[(str:name,float:score),...],...]
    leaderboards=[]
    try:
        file=open("leaderboards.txt")
        leaderboards=file.readlines()
        file.close()
        for line in range(len(leaderboards)):
            # leaderboards[line]=leaderboards[line][0:-1] # turns each line into a string (character array) # there's no way this is necessary, keeping just incase
            leaderboards[line]=leaderboards[line].split("|") # splits the category from the corresponding scores
            leaderboards[line][0]=[int(param) for param in leaderboards[line][0].split(",")] # formats into [rows,columns,mines]
            leaderboards[line][1]=[(entry[0],float(entry[1])) for entry in [entry.split(":") for entry in leaderboards[line][1].split(",")]] # formats into list of (str:name,float:score)
    finally:
        return leaderboards # if file not found or corrupt

def empty_leaderboards(): # clears the leaderboards
    file=open("leaderboards.txt","w")
    file.truncate()
    file.close()
    present()

# ---------------------------------------------------------------------------------------------------------------- #
#                                                       Run                                                        #
# ---------------------------------------------------------------------------------------------------------------- #

state={"name":"","rows":10,"columns":10,"mines":10}
menu() # runs the menu
window.mainloop() # gets the gui going

# ---------------------------------------------------------------------------------------------------------------- #