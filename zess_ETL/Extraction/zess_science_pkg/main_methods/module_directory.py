import os

def main(root_dir, main_dir, main_dir_names):
    #Create the directories
    for i in range(0, len(main_dir)):
	    for j in range(0,len(main_dir[i])):
		    dirName = f"{str(root_dir)}/{str(main_dir_names[i])}/{str(main_dir[i][j])}"

		    try:
		        # Create target Directory
		        os.makedirs(dirName)
		        print(f"Directory {dirName} Created ")
		    except FileExistsError:
		        print(f"Directory {dirName} already exists")

		    # Create target Directory if don't exist
		    if not os.path.exists(dirName):
		        os.makedirs(dirName)
		        print(f"Directory {dirName} Created ")
		    else:
		        print(f"Directory {dirName} already exists")

if __name__ == '__main__':
    main()
