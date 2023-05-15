from py4web.core import Template, action

def render_template(data, html, path=None):
    print (path)
    context = dict(output=data)
    Template(html, path).on_success(context)
    return context['output']

