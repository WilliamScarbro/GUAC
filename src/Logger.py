from tqdm import tqdm

class Logger:
    def __init__(self,iterations,verbose_arg):
        self.pbar=tqdm(total=iterations,ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
        self.messages=[]
        self.verbose_arg=verbose_arg

    def log(self,message,verbose=0):
        #print(f"{self.verbose_arg}>={verbose}?")
        if self.verbose_arg<verbose:
            return
        
        self.pbar.clear(nolock=False)

        print(message)
        
        self.pbar.refresh(nolock=False)

    def update(self):
        self.pbar.update(1)

    def close(self):
        self.pbar.close()
