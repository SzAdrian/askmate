from flask import Flask, render_template, request, redirect, url_for
import data_handler
import util

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def route_last_five_questions():
    sorted_questions = data_handler.get_latest_five_questions()
    return render_template(url_for("index.html", questions=sorted_questions))


@app.route('/list', methods=["GET", "POST"])
def route_list():
    search_options = data_handler.SEARCH_OPTIONS
    order_options = data_handler.ORDER_OPTIONS

    selected_o_option = request.args.get("order_direction")
    selected_s_option = request.args.get("ordered_by")
    try:
        order_direction = util.OPTIONS[request.args.get("order_direction")]
        ordered_by = util.OPTIONS[request.args.get("ordered_by")]
    except KeyError:
        order_direction = "DESC"
        ordered_by = "submission_time"

    sorted_questions = data_handler.sort_questions(ordered_by,order_direction)
    return render_template("list.html", questions=sorted_questions, s_options=search_options, o_options=order_options, selected_s_option=selected_s_option,selected_o_option=selected_o_option)

@app.route("/question/<question_id>", methods=["GET", "POST"])
def route_question(question_id):
    question = data_handler.get_data_by_id(question_id,'question')[0]
    print(question)
    if request.method == "GET":

        question["view_number"] = int(question["view_number"]) + 1
        data_handler.edit_row('question',question)

    id = data_handler.get_next_id("answer")

    #question["submission_time"] = time.ctime(int(question["submission_time"]))
    answers = data_handler.get_answers_by_qid(question_id)
    return render_template("question.html", question=question, answers=answers, id=str(id))


@app.route("/add-question", methods=["GET", "POST"])
def route_add_question():
    if request.method == "POST":

        data_handler.add_new_row_to_table(request.form, "question")
        return redirect(url_for("route_question", question_id=request.form.get("id")))
    id = data_handler.get_next_id("question")
    empty_question = {}
    return render_template("add-question.html", id=str(id), question=empty_question)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def route_new_answer(question_id):
    data_handler.add_new_row_to_table(request.form,"answer")
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<question_id>/delete", methods=["GET", "POST"])
def route_delete_question(question_id):
    data_handler.delete_data_by_id(question_id,"question")
    return redirect(url_for("route_list"))


@app.route("/answer/<answer_id>/delete", methods=["GET", "POST"])
def route_delete_answer(answer_id):
    answer = data_handler.get_data_by_id(answer_id,'answer')[0]
    question_id = answer.get('question_id')
    data_handler.delete_data_by_id(str(answer.get("id")),"answer")
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def route_edit(question_id):
    if request.method == "POST":
        data_handler.edit_row("question", request.form)
        return redirect(url_for("route_question", question_id=request.form.get("id")))

    question = data_handler.get_data_by_id(question_id,'question')[0]
    return render_template("add-question.html", question=question)


@app.route("/question/<question_id>/vote-up", methods=["GET", "POST"])
def route_question_vote_up(question_id):
    question = data_handler.get_data_by_id(question_id,'question')[0]
    question["vote_number"] = int(question["vote_number"]) + 1
    question["view_number"] = int(question["view_number"]) - 1
    data_handler.edit_row("question",question)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/question/<question_id>/vote-down", methods=["GET", "POST"])
def route_question_vote_down(question_id):
    question = data_handler.get_data_by_id(question_id,'question')[0]
    question["vote_number"] = int(question["vote_number"]) - 1
    question["view_number"] = int(question["view_number"]) - 1
    data_handler.edit_row("question",question)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/answer/<answer_id>/vote-up", methods=["GET", "POST"])
def route_answer_vote_up(answer_id):
    answer = data_handler.get_data_by_id(answer_id,'answer')[0]
    question_id = str(answer["question_id"])
    answer["vote_number"] = int(answer["vote_number"]) + 1
    question = data_handler.get_data_by_id(question_id,'question')[0]
    question["view_number"] = int(question["view_number"]) - 1
    data_handler.edit_row("question",question)
    data_handler.edit_row("answer",answer)
    return redirect(url_for("route_question", question_id=question_id))


@app.route("/answer/<answer_id>/vote-down", methods=["GET", "POST"])
def route_answer_vote_down(answer_id):
    answer = data_handler.get_data_by_id(answer_id,'answer')[0]
    question_id = str(answer["question_id"])
    answer["vote_number"] = int(answer["vote_number"]) - 1
    question = data_handler.get_data_by_id(question_id,'question')[0]
    question["view_number"] = int(question["view_number"]) - 1
    data_handler.edit_row("question", question)
    data_handler.edit_row("answer", answer)
    return redirect(url_for("route_question", question_id=question_id))


if __name__ == '__main__':
    app.run(
        port=5000,
        debug=True,
    )
