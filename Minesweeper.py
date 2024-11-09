from tkinter import Tk,Frame,Label,Entry,Button,PhotoImage,Canvas,Scrollbar # GUI library
import tkinter.font as Font
from random import randint # placing mines
from time import time # timer

root=Tk() # window
root.geometry(f"720x720+{root.winfo_screenwidth()//2-360}+{root.winfo_screenheight()//2-360}")
root.frame=Frame(root)
root.frame.pack()

explosion_pic=PhotoImage(master=root,file="explosion.png") # loading images
flag_pic=PhotoImage(master=root,file="flag.png")
mine_pic=PhotoImage(master=root,file="mine.png")
flagged_mine_pic=PhotoImage(master=root,file="flagged_mine.png")

colours=["blue","green","red","magenta","maroon","#0db879","grey","black"]

# TODO: check all spacing/layout is still okay in windows
# TODO: runs very slow for big grids, was it running faster on pc before & if it was, was it more efficient or just a faster pc?

# ---------------------------------------------------------------------------------------------------------------- #
#                                                     Pre-game                                                     #
# ---------------------------------------------------------------------------------------------------------------- #

def menu(): # displays menu
    state["game over"]=True # stop clock updating if came here from reset button
    [widget.destroy() for widget in root.frame.winfo_children()] # clear window
    Label(root.frame).grid() # spacer
    inputs=[None]*4
    for i,key in zip(range(4),state): # these are the text fields for the menu (name,rows,columns,mines)
        Label(root.frame,text=key).grid()
        inputs[i]=Entry(root.frame)
        inputs[i].insert(0,state[key])
        inputs[i].grid(row=i+1,column=1)
    Label(root.frame).grid() # spacer
    Button(root.frame,text="Start",command=lambda:setup(inputs)).grid()
    Button(root.frame,text="Leaderboards",command=present).grid(row=6,column=1)

def setup(inputs): # validates menu input & sets up button grid
    size=Font.nametofont("TkDefaultFont").metrics("linespace")+4 # smallest size square we can get grid spaces
    maximums=[None,root.winfo_height()//size-4,root.winfo_width()//size-2,"rows×columns"]
    message=""
    for i,key in zip(range(4),state): # validate input
        state[key]=inputs[i].get()
        if i==0: # for name input
            if len(state["name"])>40:
                message+="name must be less than 40 characters\n"
            continue # skip numerical validation for name
        if not state[key].isdigit():
            message+=key+" must be an integer\n"
            continue # skip numerical comparisons if not an int
        state[key]=int(state[key])
        if state[key]==0 or (type(maximums[i])==int and state[key]>maximums[i]): # can't be 0, only apply limit if calculated
            message+=f"{key} must be between 1 & {maximums[i]}\n"
        if i==2: # after validating name, rows & columns
            # only calculate mine limit if no numerical validation issues so far
            if message=="" or message=="name must be less than 40 characters\n":
                maximums[3]=state["rows"]*state["columns"]-1
    if "rows must be between" in message or "columns must be between" in message:
        message+="you can change grid size limits by resizing this window\n"
    [widget.destroy() for widget in root.frame.winfo_children()] # clear window
    if message: # show input validation message if there is one
        message=message[:-1] # remove last \n char
        Label(root.frame).grid() # spacer
        Label(root.frame,text=message).grid()
        Label(root.frame).grid() # spacer
        Button(root.frame,text="Okay",command=menu).grid()
        return

    state["first click"]=True # mines are placed & timer starts on first click
    state["game over"]=False # game mechanic functions won't work when game over

    # creates & displays button grid & binds functions to button mouse events
    Label(root.frame).grid() # spacer
    minefield=Frame(root.frame,bg="#777")
    minefield.grid(columnspan=2)
    state["buttons"]=[[None]*state["columns"] for r in range(state["rows"])]
    for row in range(state["rows"]):
        pad_y=(int(row==0),1)
        for column in range(state["columns"]):
            state["buttons"][row][column]=Label(minefield,text="",bg="#aaa",bd=0,highlightthickness=0)
            state["buttons"][row][column].grid(row=row,column=column,padx=(int(column==0),1),pady=pad_y,ipadx=0,ipady=0,sticky="nsew")
            state["buttons"][row][column].bind("<Button-1>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<Button-3>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<ButtonRelease-1>",lambda event,row=row,column=column:reveal(event,row,column))
            state["buttons"][row][column].bind("<ButtonRelease-3>",lambda event,row=row,column=column:flag(row,column))
    [minefield.rowconfigure(row,minsize=size,uniform="button") for row in range(state["rows"])]
    [minefield.columnconfigure(column,minsize=size,uniform="button") for column in range(state["columns"])]
    Label(root.frame).grid() # spacer
    Button(root.frame,text="Reset",command=menu,width=5).grid() # TODO: make sure this has the same symmetry in windows
    root.frame.grid_columnconfigure(0,weight=1) # reset button takes up the whole width for now
    root.frame.grid_columnconfigure(1,weight=0)
    state["time label"]=Label(root.frame)
    state["time label"].grid(columnspan=2)

def start(row,column): # places mines & starts timer
    state["first click"]=False
    # U=unclicked empty space
    # M=unclicked mine
    # [empty string]=empty space with no adjacent mines
    # [number n from 1-8]=empty space with n adjacent mines
    # FM=correctly flagged mine
    # FF=incorrectly flagged empty space
    state["grid"]=[["U"]*state["columns"] for r in range(state["rows"])] # <-- creates empty grid
    mine_counter=state["mines"]
    while mine_counter>0:
        random_row=randint(0,state["rows"]-1)
        random_column=randint(0,state["columns"]-1)
        if state["grid"][random_row][random_column]=="U" and (random_row,random_column)!=(row,column):
            state["grid"][random_row][random_column]="M"
            mine_counter-=1
    state["start time"]=time()
    update_timer()

# ---------------------------------------------------------------------------------------------------------------- #
#                                             Game Mechanic Functions                                              #
# ---------------------------------------------------------------------------------------------------------------- #

def update_timer(): # updates timer label & schedules next update for a second later
    if state["game over"]: return # doesn't run if game over
    state["time label"].config(text=f"{int(round(time()-state["start time"]))}s") # update label
    wait=(state["start time"]-time())%1 # update interval is independent of calculation time
    root.after(int((1000*wait)//1),update_timer) # schedule next update

def clicked(row,column): # changes button colour on mousedown
    if state["game over"]: return # doesn't run if game over
    # first click is in the below condition because state["grid"] doesn't exist yet on first click
    if state["first click"] or state["grid"][row][column] in ["U","M","FF","FM"]:
        state["buttons"][row][column].config(bg="#888")

def reveal(event,row,column): # reveals if space is mine (game over) or empty (calls reveal_more)
    if event.state&12: # ctrl/cmd+click flags the space instead
        flag(row,column)
        return
    if state["game over"]: return # doesn't run if game over
    if state["first click"]: start(row,column) # mines are placed & timer starts on first click
    if state["grid"][row][column]=="U": # if space is empty call reveal_more then check if game is won
        reveal_more(row,column)
        check()
    elif state["grid"][row][column]=="M": # if there's a mine game over
        state["buttons"][row][column].config(image=explosion_pic,bg="#ccc")
        state["grid"][row][column]="*" # so it doesn't get shown as an unexploded mine in the game over mine reveal
        end(True)
    elif state["grid"][row][column] in ["FF","FM"]: # change button colour back to normal on mouseup
        state["buttons"][row][column].config(bg="#aaa")

def reveal_more(row,column): # reveals number of adjacent mines, if 0 then repeat for all adjacent spaces
    to_do=[(row,column)] # stack of spaces to be revealed
    while to_do:
        row,column=to_do.pop()
        adjacent_mines=0
        new_places=0
        for scan_row in range(3): # for each row in surrounding 3x3 square
            if(row==0 and scan_row==0) or (row==state["rows"]-1 and scan_row==2):
                continue # ^skip 1st scan_row if at top or last scan_row if at bottom
            for scan_column in range(3):
                if(column==0 and scan_column==0) or (column==state["columns"]-1 and scan_column==2) or (scan_row,scan_column)==(1,1):
                    continue # ^skip 1st scan_column if at left side or last scan_column if at right side, also skip current space
                adjacent_space=state["grid"][row+scan_row-1][column+scan_column-1]
                adjacent_space_coords=(row+scan_row-1,column+scan_column-1)
                if adjacent_space in ["M","FM"]: # if adjacent space is a mine, increment adjacent mines
                    adjacent_mines+=1
                # if no adjacent mines (yet) & an adjacent space is unclicked & not already on the to do list
                elif adjacent_mines==0 and adjacent_space=="U" and adjacent_space_coords not in to_do:
                    to_do.append((row+scan_row-1,column+scan_column-1)) # put it in the to do list
                    new_places+=1 # count how many spaces added to to_do incase they need removed
        if adjacent_mines>0: # if there are adjacent mines
            if new_places: del to_do[-new_places:] # don't reveal adjacent spaces by removing any spaces added to to_do from this iteration
            state["grid"][row][column]=str(adjacent_mines) # update grid
            state["buttons"][row][column].config(text=state["grid"][row][column],
                font=("Helvetica",11,"bold"),fg=colours[adjacent_mines-1],bg="#ccc")
        else:
            state["grid"][row][column]="" # update grid
            state["buttons"][row][column].config(bg="#ccc")

def flag(row,column): # flags/unflags a space
    if state["game over"]: return # doesn't run if game over
    if state["first click"]: start(row,column) # mines are placed & timer starts on first click
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
    check() # check if game is won

def check(): # checks if the game is won
    empty_spaces_unclicked=False # there are 2 ways to win, reveal all empty spaces or correctly flag all mines
    flags_incomplete=False
    for row in state["grid"]:
        for space in row:
            if space=="FF": # both winning conditions are failed if there are any incorrect flags
                return
            if space=="U": # unrevealed empty space
                empty_spaces_unclicked=True
            elif space=="M": # unflagged mine
                flags_incomplete=True
            if empty_spaces_unclicked and flags_incomplete: # leave the check when both winning conditions are failed
                return
    end(False) # game is won

def end(lost): # stops timer, reveals mines & adds button to submit time to leaderboards if you win
    state["time taken"]=round(time()-state["start time"],3) # record time
    state["game over"]=True
    [[state["buttons"][r][c].config(image=mine_pic if state["grid"][r][c]=="M" # reveal mines
        else (flagged_mine_pic if state["grid"][r][c]=="FM" else None))
        for c in range(state["columns"])] for r in range(state["rows"])]
    if lost: return # nothing more to do if player lost
    state["time label"].config(text=(f"Player time: {state["time taken"]}s")) # shows your time
    Button(root.frame,text="Submit",command=submit,width=5).grid(row=3,column=1)
    root.frame.grid_columnconfigure(1,weight=1)

# ---------------------------------------------------------------------------------------------------------------- #
#                                                   Leaderboards                                                   #
# ---------------------------------------------------------------------------------------------------------------- #

def submit(): # adds score to leaderboards
    leaderboards=access() # get leaderboards from file
    if leaderboards==[]: # if file not found/empty then create/overwrite with new one
        file=open("leaderboards.txt","w")
        file.write(f"{state["rows"]},{state["columns"]},{state["mines"]}|{state["name"]}:{state["time taken"]}\n")
        file.close()
        return
    player_category=(state["rows"],state["columns"],state["mines"])
    player_score=(state["name"],state["time taken"])
    player_grid_size=state["rows"]*state["columns"] # categories are ranked by grid size then mine count
    for i,[[rows,columns,mines],scores] in enumerate(leaderboards): # for each category
        grid_size=rows*columns
        if player_grid_size>grid_size: # if grid size bigger than this category, insert new category here & break
            leaderboards.insert(i,[player_category,[player_score]])
            break
        if player_grid_size==grid_size: # grid size equal to this category
            if state["mines"]>mines: # if mine count more than this category, insert new category here & break
                leaderboards.insert(i,[player_category,[player_score]])
                break
            if state["mines"]==mines: # grid size & mine count equal to this category
                if state["rows"]!=rows: # if grid dimensions different, insert new category here & break
                    leaderboards.insert(i,[player_category,[player_score]])
                    break
                # get first index where player time faster than this time or get len(scores) if player time is slowest
                player_rank=next((j for j,(name,time_taken) in enumerate(scores) if state["time taken"]<time_taken),len(scores))
                leaderboards[i][1].insert(player_rank,player_score) # insert score here & break
                break
        if i==len(leaderboards)-1: # if grid size smaller than last category, append new category & break
            leaderboards.append([player_category,[player_score]])
            break # without this break it goes through the loop again for the new category & adds the entry again
    file_string=""
    for [rows,columns,mines],scores in leaderboards: # format leaderboards to string for txt file
        file_string+=f"{rows},{columns},{mines}|"
        for name,time_taken in scores:
            file_string+=f"{name}:{time_taken},"
        file_string=file_string[:-1]+"\n"
    file=open("leaderboards.txt","w")
    file.truncate()
    file.write(file_string) # overwrite file
    file.close()
    present(leaderboards) # show leaderboards

def mouse_scroll(event,canvas): # scrolls leaderboards on mouse wheel event
    canvas.yview_scroll(-event.delta,"units") # TODO: may need scaling factor for windows (as opposed to macos)

def present(leaderboards=None): # displays the leaderboards
    [widget.destroy() for widget in root.frame.winfo_children()] # clear window
    Label(root.frame).grid() # spacer
    if leaderboards==None: # if came here from menu, get leaderboards from file
        leaderboards=access()
    if leaderboards==[]: # if file not found/empty
        Label(root.frame,text="There are no leaderboard entries").grid()
        Label(root.frame).grid() # spacer
        Button(root.frame,text="Back",command=menu).grid()
        return
    Label(root.frame,text="Player",bg="#777",width=50).grid(padx=1,sticky="ew") # column names
    Label(root.frame,text="Time",bg="#777",width=15).grid(row=1,column=1,padx=1,sticky="ew")
    Label(root.frame).grid() # spacer
    canvas=Canvas(root.frame,yscrollincrement=2) # tkinter canvas is scrollable
    canvas.grid(columnspan=2)
    boardframe=Frame(canvas) # this is where the actual tables are put on screen

    line=0
    for i,[[rows,columns,mines],scores] in enumerate(leaderboards): # for every category
        Label(boardframe,text=f"{rows}×{columns} grid, {mines} mines").grid(row=line,columnspan=2) # category headers
        line+=1
        for name,time_taken in scores: # for every entry
            Label(boardframe,text=name,bg="#777",width=50).grid(row=line,padx=1,pady=1)
            # format time taken as "{hours}h {minutes}m {seconds.milliseconds}s"
            hours=f"{int(time_taken//3600)}h " if time_taken>=3600 else ""
            minutes=f"{int(time_taken%3600//60)}m " if time_taken>=60 else ""
            seconds=f"{round(time_taken%60,3)}s"
            Label(boardframe,text=hours+minutes+seconds,bg="#777",width=15).grid(row=line,column=1,padx=1)
            line+=1
        if i==len(leaderboards)-1: break # skip spacer after last category
        Label(boardframe).grid() # spacer for gaps between categories
        line+=1

    canvas.create_window((0,0),window=boardframe,anchor="nw") # scrollable medium to view boardframe through instead of rendering with a geometry manager
    boardframe.update_idletasks() # render any pending geometry changes immediately (required for scrolling), also gives us boardframe height
    if boardframe.winfo_height()>root.winfo_height()-7*root.frame.winfo_children()[0].winfo_height(): # if boardframe too big to show all at once
        scrollbar=Scrollbar(root.frame,command=canvas.yview) # scrollbar updates canvas yview # TODO: test scrolling on windows
        scrollbar.grid(row=3,column=2,sticky="ns") # scrollbar fits to height of canvas' grid row
        canvas.config(yscrollcommand=scrollbar.set,scrollregion=canvas.bbox("all"), # canvas yview updates scrollbar,limit scrollregion
            width=boardframe.winfo_width()-6,height=root.winfo_height()-7*root.frame.winfo_children()[0].winfo_height()) # limit size of canvas to fit window
        canvas.bind_all("<MouseWheel>",lambda event:mouse_scroll(event,canvas)) # mouse wheel updates canvas yview
    else:
        canvas.config(width=boardframe.winfo_width()-6,height=boardframe.winfo_height())
    Label(root.frame).grid() # spacer
    Button(root.frame,text="Clear leaderboards",command=empty_leaderboards).grid()
    Button(root.frame,text="Back",command=menu).grid(row=5,column=1)

def access(): # reads the file & formats into list of [[rows,columns,mines],[list of (str:name,float:score)]]
    leaderboards=[]
    try:
        file=open("leaderboards.txt")
        leaderboards=file.readlines()
        file.close()
        for line in range(len(leaderboards)):
            leaderboards[line]=leaderboards[line].split("|") # split category from corresponding scores
            leaderboards[line][0]=[int(param) for param in leaderboards[line][0].split(",")] # format into [rows,columns,mines]
            # format into list of (str:name,float:score)
            leaderboards[line][1]=[(entry[0],float(entry[1])) for entry in [entry.split(":") for entry in leaderboards[line][1].split(",")]]
    finally:
        return leaderboards # if file not found return []

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
root.mainloop() # gets the gui going

# ---------------------------------------------------------------------------------------------------------------- #