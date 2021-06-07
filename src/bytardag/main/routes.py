from bytardag.main import bp


@bp.route("/")
def index():
    return "Hello World!"
