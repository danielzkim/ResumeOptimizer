from flask import Flask, render_template, request
import fitz
from openai import OpenAI
import markdown2


app = Flask(__name__)

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="put_your_key_here",
)

system_instructions = """
You are a resume optimizer.
 You are responsible for optimizing a given resume for a specific role at a specific company. 
 You are given a resume, a role, and a company. 
 The main objective is getting the given resume to pass an ATS filter, 
 and maximize the probability of the user getting their desired job.
 Only respond with a markdown-formatted optimized resume (with no commentary).
 
 ###
 Desired Job Role:
 {role}
 
 ###
 Desired Company:
 {company}
 
 ###
 Resume:
 {resume}

 ###
 Optimized Resume:
 """

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # gets the pdf file from the http request
        pdf_file = request.files['pdf_file']
        pdf_file.save('tmp.pdf')

        # opens the pdf file and reads the text using fitz parser
        doc = fitz.open('tmp.pdf')
        text = ''
        for page in doc:
            text += page.get_text()

        # get the company and role from the form
        company = request.form.get('company')
        role = request.form.get('role')

        # ask chatgpt to optimize the resume per the instructions
        model_output = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": system_instructions.format(resume=text, role=role, company=company),
                }
            ],
            model="gpt-3.5-turbo",
        )
        model_output = model_output.choices[0].message.content
        markdown = markdown2.Markdown()
        html = markdown.convert(model_output)
        return render_template('index.html', optimized_resume=html)
        # breakpoint()
        # # Parse the model output and convert it back into a PDF
        # optimized_resume = model_output['choices'][0]['message']['content']
        # markdown = markdown2.Markdown()
        # html = markdown.convert(optimized_resume)

        # # Use pdfkit to convert HTML to PDF
        # pdfkit.from_string(html, 'optimized_resume.pdf')

        # # TODO: return the pdf file to the user/FE

        # return model_output

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
