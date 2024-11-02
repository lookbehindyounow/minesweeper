from tkinter import Tk,Frame,Label,Entry,Button,PhotoImage,Scrollbar # GUI library
from random import randint # placing mines
from time import time,sleep # timer

window=Tk() # window
window.geometry(f"720x720+{window.winfo_screenwidth()//2-360}+{window.winfo_screenheight()//2-360}")
window.frame=Frame(window)
window.frame.pack()

explosion_pic=PhotoImage(master=window,width=16,height=17,file="explosion.png") # loading images
flag_pic=PhotoImage(master=window,width=16,height=17,file="flag.png")
mine_pic=PhotoImage(master=window,width=16,height=17,file="mine.png")
flagged_mine_pic=PhotoImage(master=window,width=16,height=17,file="flagged_mine.png")

state={"name":"","rows":10,"columns":10,"mines":10}

# ---------------------------------------------------------------------------------------------------------------- #
#                                                     Pre-game                                                     #
# ---------------------------------------------------------------------------------------------------------------- #

def menu(): # displays menu
    [widget.destroy() for widget in window.frame.winfo_children()] # get rid of whatever was in canvas before putting something new in
    if (window.winfo_width(),window.winfo_height())!=(720,720):
        window.geometry("720x720") # resizing if necessary
    Label(window.frame).grid() # spacer
    inputs=[None]*4
    for i,key in zip(range(4),state): # these are the text fields for the menu
        Label(window.frame,text=key).grid()
        inputs[i]=Entry(window.frame)
        inputs[i].insert(0,state[key])
        inputs[i].grid(row=i,column=1)
    Label(window.frame).grid() # spacer
    Button(window.frame,text="Start",command=lambda:setup(inputs)).grid()
    Button(window.frame,text="Leaderboards",command=present_no_gui).grid(row=6,column=1)

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

    # displays button grid & binds functions to mouse events
    Label(window.frame).grid() # spacer
    minefield=Frame(window.frame)
    minefield.grid()
    state["buttons"]=[[Label(minefield,text="",relief="raised",height=1,width=2)]*state["columns"]]*state["rows"] # creates 2d-array of buttons
    for row in range(state["rows"]):
        for column in range(state["columns"]):
            state["buttons"][row][column].grid(row=row,column=column)
            state["buttons"][row][column].bind("<Button-1>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<Button-3>",lambda event,row=row,column=column:clicked(row,column))
            state["buttons"][row][column].bind("<ButtonRelease-1>",lambda event,row=row,column=column:reveal(row,column))
            state["buttons"][row][column].bind("<ButtonRelease-3>",lambda event,row=row,column=column:flag(row,column))
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
    state["grid"]=[["U"]*state["columns"]]*state["rows"] # <-- creates empty grid
    mine_counter=state["mines"]
    while mine_counter>0:
        random_row=randint(0,state["rows"]-1)
        random_column=randint(0,state["columns"]-1)
        if state["grid"][random_row][random_column]=="U" and (random_row,random_column)!=(row,column):
            state["grid"][random_row][random_column]="M"
            mine_counter-=1
    state["start time"]=time()
    update_timer()

def update_timer():
    if state["game over"]: return
    state["time label"].config(text=str(round(time()-state["start time"],0))[0:-2]+"s")
    wait=1000*round((state["start time"]-time())%1,3) # keeps the timer synched with actual time
    window.after(int(wait),update_timer) # keeps the timer updating

def clicked(row,column): # buttons go down when you click them but don't reveal/flag until you let go
    if state["game over"]: return
    try:
        if state["grid"][row][column] in ["U","M","FF","FM"]: # only if unclicked & the game is still going
            state["buttons"][row][column].config(relief=SUNKEN)
    except NameError: # TODO: test without exceptions & find cause of any present errors
        state["buttons"][row][column].config(relief=SUNKEN)
    except IndexError:
        state["buttons"][row][column].config(relief=SUNKEN)

def reveal(row,column):
    if state["game over"]: return
    if state["first click"]: # changes the detection boolean, calls the function to place the mines & starts the timer
        state["first click"]=False
        start(row,column)
        state["start time"]=time()
        update_timer()
    if state["grid"][row][column]in["U","FF"]: # if there's no mine to to the revealing algorithm
        iterative_reveal(row,column)
    elif state["grid"][row][column]in["M","FM"]: # if there's a mine game over
        state["game over"]=True
        state["buttons"][row][column].config(image=explosion_pic,width=16,height=17)
        state["grid"][row][column]="*" # so it doesn't get shown as an unexploded mine in the game over mine reveal
        end(False)
    check()

def recursive_reveal(row,column): # old method of doing the reveal, not in use but still works as an alternate method
    state["grid"][row][column]=""          # to iterative_reveal (below)
    adjacent_mines=0
    for vertical in range(3): # each iteration scans a row in the surrounding 3x3 square
        if(row==0 and vertical==0)or(row==state["rows"]-1 and vertical==2): # skip 1st row scan if we're at the top
            continue                                               # or last row scan if we're at the bottom
        for horizontal in range (3): # the next 3 lines are the same stuff but for columns
            if(column==0 and horizontal==0)or(column==state["columns"]-1 and horizontal==2):
                continue
            if state["grid"][row+vertical-1][column+horizontal-1]in["M","FM"]: # adjacent mine counter
               adjacent_mines+=1
    if adjacent_mines>0:
        state["grid"][row][column]=str(adjacent_mines) # update grid
    state["buttons"][row][column].config(text=state["grid"][row][column], # show on screen with coloured numbers
                                fg=["white","blue","green","red","magenta","maroon","#0db879",
                                    "grey","black"][adjacent_mines],font=("Helvetica",9,"bold"),
                                relief=FLAT,image="",width=2,height=1)
    if adjacent_mines==0: # with this method it's easier to do the adjacent scan twice because of the fact the
                          # recursion happens in this nested loop & we need to know if there are any adjacent mines
                          # before we even do anything here
        for vertical in range(3):
            if(row==0 and vertical==0)or(row==state["rows"]-1 and vertical==2):
                continue
            for horizontal in range (3):
                if(column==0 and horizontal==0)or(column==state["columns"]-1 and horizontal==2):
                    continue # ↓recalls itself for all scanned unclicked squares
                if state["grid"][row+vertical-1][column+horizontal-1]=="U":
                    # window.update() # unhash these 2 lines to show the recursive reveal path
                    # sleep(0.01)
                    recursive_reveal(row+vertical-1,column+horizontal-1)

def iterative_reveal(row,column): # more memory efficient method I think? defo seems faster too
    to_do=[(row,column)] # effectively a stack of the squares that need revealed
    while True:
        location=min(to_do)      # prioritises to do list of squares to reveal from the top down to save memory
        to_do.remove(min(to_do)) # (without this it's a very perculiar search path)
        state["grid"][location[0]][location[1]]=""
        adjacent_mines=0
        new_places=0
        for vertical in range(3): # each iteration scans a row in the surrounding 3x3 square
            if(location[0]==0 and vertical==0)or(location[0]==state["rows"]-1 and vertical==2):
                continue # ^skip 1st row scan if we're at the top or last row scan if we're at the bottom
            for horizontal in range (3): # the next 3 lines are the same stuff but for columns
                if(location[1]==0 and horizontal==0)or(location[1]==state["columns"]-1 and horizontal==2):
                    continue
                if state["grid"][location[0]+vertical-1][location[1]+horizontal-1]in["M","FM"]: # adjacent mine counter
                    adjacent_mines+=1
                if state["grid"][location[0]+vertical-1][location[1]+horizontal-1]=="U":        # nested conditions to fit
                    if (location[0]+vertical-1,location[1]+horizontal-1) not in to_do: # the rest of the code
                        # ^if an adjacent square is unclicked & not already on the to do list
                        to_do.append((location[0]+vertical-1,location[1]+horizontal-1)) # put it in the to do list
                        new_places+=1 # & count how many new items were just put in incase they need removed
        if adjacent_mines>0: # in the event that the current square is numbered & not blank
            for i in range(new_places): # remove the newly added squares from the to do list
                to_do.pop()
            state["grid"][location[0]][location[1]]=str(adjacent_mines) # update grid
        state["buttons"][location[0]][location[1]].config(text=state["grid"][location[0]][location[1]],
                                                 fg=["white","blue","green","red","magenta","maroon","#0db879",
                                                     "grey","black"][adjacent_mines],font=("Helvetica",9,"bold"),
                                                 relief=FLAT,image="",width=2,height=1)
        # window.update() # unhash these 2 lines to show the iterative reveal path (kind of boring when it's top down)
        # sleep(0.01)
        if len(to_do)==0:
            break # finish when to do list empties

def flag(row,column): # puts a flag when you right click
    if state["game over"]: return
    if state["first click"]:
        state["first click"]=False
        start(row,column)
        state["start time"]=time()
        update_timer()
    if state["grid"][row][column]=="M":
        state["grid"][row][column]="FM"
        state["buttons"][row][column].config(image=flag_pic,relief=RAISED,width=16,height=17)
    elif state["grid"][row][column]=="U":
        state["grid"][row][column]="FF"
        state["buttons"][row][column].config(image=flag_pic,relief=RAISED,width=16,height=17)
    elif state["grid"][row][column]=="FM":
        state["grid"][row][column]="M"
        state["buttons"][row][column].config(image="",relief=RAISED,width=2,height=1)
    elif state["grid"][row][column]=="FF":
        state["grid"][row][column]="U"
        state["buttons"][row][column].config(image="",relief=RAISED,width=2,height=1)
    check()

def check(): # this is called after every square clicked & it checks if the game's finished
    if state["game over"]: return
    game_over_brute=True # there are 2 ways to win, flag all mines or clear all empty spaces
    game_over_flag=True
    for row in state["grid"]:
        for column in row:
            if column in["FF","U"]: # any empty spaces left un-revealed & you can't brute-force win
                game_over_brute=False
            if column in["FF","M"]: # any incorrect flags or mines that aren't flagged & you can't flag win
                game_over_flag=False
            if not game_over_brute and not game_over_flag: # leave the loop after both winning conditions aren't
                break                                      # met to save time
        if not game_over_brute and not game_over_flag:
            break
    if game_over_brute or game_over_flag: # stop the timer & end the game when you win
        state["time taken"]=round(time()-state["start time"],3)
        state["game over"]=True
        end(True)

# ---------------------------------------------------------------------------------------------------------------- #
#                                                    Game Over                                                     #
# ---------------------------------------------------------------------------------------------------------------- #

def end(win):
    for row in range(len(state["rows"])): # reveals where the mines were
        for column in range(len(state["columns"])):
            if state["grid"][row][column]=="M":
                state["buttons"][row][column].config(image=mine_pic,width=16,height=17)
            if state["grid"][row][column]=="FM":
                state["buttons"][row][column].config(image=flagged_mine_pic,width=16,height=17)
    if win:
        state["time label"].config(text=("Player time: "+str(state["time taken"])+"s")) # shows your time
        # TODO: add a button to add your score to leaderboard optionally
        leaderboards=access() # get the leaderboards table from file
        if leaderboards is not None:
            player_mode_rank=[state["rows"]*state["columns"],state["mines"]] # leaderboards are organised by rank - grid size & then mine count
            new_leaderboards=[]
            overwritten=False # this table is a list with sections & this boolean makes life easier
            for mode in leaderboards: # for each grid size & mine count combo
                mode_rank=[mode[0][0]*mode[0][1],mode[0][2]] # for comparison to our new time
                if player_mode_rank[0]>mode_rank[0]and not overwritten: # time is for a new grid size or previous
                    new_leaderboards.append([[state["rows"],state["columns"],state["mines"]],[(state["name"],state["time taken"])]]) # grid size with lowest
                    overwritten=True                                                     # mine count
                if player_mode_rank[0]==mode_rank[0]and not overwritten: # time is for the current grid size
                    if player_mode_rank[1]>mode_rank[1]: # time is for a new mine count
                        new_leaderboards.append([[state["rows"],state["columns"],state["mines"]],[(state["name"],state["time taken"])]])
                        overwritten=True
                    if player_mode_rank[1]==mode_rank[1]: # time is for the current mine count
                        new_mode=[]
                        for score in mode[1]: # for each time in rank
                            if state["time taken"]<score[1]and not overwritten:
                                new_mode.append((state["name"],state["time taken"])) # put time into new table section
                                overwritten=True
                            new_mode.append(score) # put existing times into new table section in order
                        if not overwritten:
                            new_mode.append((state["name"],state["time taken"])) # put time on at the end if it's the slowest
                            overwritten=True
                        mode[1]=new_mode # replace old table with new table for this rank
                new_leaderboards.append(mode) # write each section to new leaderboard table in order
            if not overwritten:
                new_leaderboards.append([[state["rows"],state["columns"],state["mines"]],[(state["name"],state["time taken"])]]) # time is for new lowest rank
            leaderboards=new_leaderboards # update leaderboards table
            
            file=open("leaderboard.txt","w") # overwrite leaderboards file with new table
            file.truncate()
            file_string=""
            for mode in leaderboards: # file formate is explained further in access()
                file_string+=str(mode[0][0])+","+str(mode[0][1])+","+str(mode[0][2])+":"
                for score in mode[1]:
                    file_string+=str(score[0])+","+str(score[1])+";"
                file_string=file_string[0:-1]+"\n"
            file.write(file_string)
            file.close()
        else:
            file=open("leaderboard.txt","w") # if there is no file then make one
            file.write(str(state["rows"])+","+str(state["columns"])+","+str(state["mines"])+":"+state["name"]+","+str(state["time taken"])+"\n")
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
        Label(window.frame,text="Player",relief=RIDGE,width=64).grid()
        Label(window.frame,text="Time",relief=RIDGE,width=15).grid(row=1,column=1)
        Label(window.frame).grid() # spacer

        boardframe=Frame(window.frame,yscrollincrement="20") # this is the object that is scrollable
        boardframe.bind_all("<MouseWheel>",lambda:mouse_scroll(boardframe)) # this is what calls the event when the mouse wheel scrolls
        boardframe.grid(columnspan=2)
        scrollbar=Scrollbar(window.frame,command=boardframe.yview) # this is the scrollbar you can click & drag
        scrollbar.grid(row=3,column=2,sticky="ns")
        boardframe.config(yscrollcommand=scrollbar.set)
        
        board=Frame(boardframe) # this is where the actual tables are put on screen
        lines=1
        for mode in leaderboards: # for every rank
            Label(board,text=str(mode[0][0])+"x"+str(mode[0][1])+" grid, "+str(mode[0][2])+" mines").grid()
            for entry in mode[1]: # for every time
                Label(board,text=entry[0],relief=RIDGE,width=64).grid()
                written_time=str(round(entry[1]%60,4))+"s" # this bit figures out if it goes into minutes or hours
                if entry[1]>=60:
                    written_time=str(int(entry[1]%3600//60))+"m "+written_time
                    if entry[1]>=3600:
                        written_time=str(int(entry[1]//3600))+"h "+written_time
                Label(board,text=written_time,relief=RIDGE,width=15).grid(row=lines,column=1)
                lines+=1
            if leaderboards.index(mode)!=len(leaderboards)-1:
                Label(board).grid() # spacer label for gaps between each board
            lines+=2
        
        boardframe.create_window((0,0),window=board,anchor="nw") # this is all more scrollbar stuff
        board.update_idletasks() # keeps the scrollbar updating
        boardframe.config(width=561,height=min(lines*21-42,538))
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

def access(): # reads the file & puts it into the nested list (table with sections)
    try:
        file=open("leaderboard.txt")
        leaderboards=file.readlines()
        file.close()
        for line in leaderboards:
            # line=line[0:-1] # turns each line into a string (character array) # there's no way this is necessary, keeping just incase
            line=line.split(":") # splits the rank from the corresponding scores
            line[0]=[int(num) for num in line[0].split(",")] # TODO: test these list comps & reformat as r,c,m|n:s,n:s,n:s...
            line[1]=[(entry[0],float(entry[1])) for entry in [entry.split(",") for entry in line[1].split(";")]]
    except:
        return [] # if there is no file or an empty/corrupt file

def empty_leaderboards(): # clears the leaderboards
    file=open("leaderboard.txt","w")
    file.truncate()
    file.close()
    present()

# ---------------------------------------------------------------------------------------------------------------- #
#                                                       Run                                                        #
# ---------------------------------------------------------------------------------------------------------------- #

menu() # runs the menu
window.mainloop() # gets the gui going

# ---------------------------------------------------------------------------------------------------------------- #