from aioconsole import aprint


class SpeechBubble:
    def __init__(self, username, text, line_length=50, inner_line_length=45):
        self.username = username
        self.text = text
        self.line_length = line_length
        self.inner_line_length = inner_line_length

    
    def wrap_multi_line(self, username, text):
        """Nitty gritty of formatting a speech bubble"""
        wrapped_text = f"{username}: "
        current_line = ""
        for word in text.split():
            if len(current_line) + len(word) > self.inner_line_length:
                if len(current_line) > 0:
                    wrapped_text += current_line + " |\n"
                current_line = f"|{word}"
            else:
                current_line += f" {word}"
    
            if len(current_line) + len(word) > self.line_length:
                wrapped_text += current_line + "\n"
                current_line = word   

        if len(current_line) > 0:
            wrapped_text += current_line
                
        return wrapped_text.strip()
    

    async def beautify(self):
        """Putting the speech bubble together"""
        top = "-" * self.line_length
        bottom = "-" * self.line_length
        body = f"| {self.wrap_multi_line(self.username, self.text)} |"
        await aprint(top)
        await aprint(body)
        await aprint(bottom)
        return top + "\n" + body + "\n" + bottom
