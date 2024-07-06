from flask import Flask, render_template, request
import vacancy_parser
import resume_parser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vacancies', methods=['GET', 'POST'])
def vacancies():
    if request.method == 'POST':
        keyword = request.form['keyword']
        area = request.form.get('area')
        salary = request.form.get('salary')
        experience = request.form.get('experience')
        vacancy_links = vacancy_parser.get_vacancy_links(keyword, area, salary, experience)
        vacancies = [vacancy_parser.get_vacancy_info(link) for link in vacancy_links]
        return render_template('vacancies.html', vacancies=vacancies)
    return render_template('search_vacancies.html')


@app.route('/resumes', methods=['GET', 'POST'])
def resumes():
    if request.method == 'POST':
        keyword = request.form['keyword']
        area = request.form.get('area')
        salary = request.form.get('salary')
        experience = request.form.get('experience')


        resume_links = resume_parser.get_resume_links(keyword, area, salary, experience)


        resumes = [resume_parser.get_resume_info(link) for link in resume_links]


        return render_template('resumes.html', resumes=resumes)
    else:

        return render_template('search_resumes.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)