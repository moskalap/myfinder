from django.shortcuts import render, HttpResponse

from wikifinder.engine.data_processor import DataProcessor

# Create your views here.

glob_mat = None
dpr = DataProcessor()


def index(request):
    if dpr.computet:
        print(dpr.glob_mat.shape)
        try:
            dpr.idf()
        except Exception:
            pass

    else:

        dpr.load_matrix_from_csv()

        print("END")

    return HttpResponse('Hello World!')


def search(request):
    parsedData = []
    if request.method == 'POST':

        q = request.POST.get('query')
        print(q)
        try:
            if not dpr.computet:
                dpr.load_matrix_from_csv()
            scr2ar = dpr.query(q)
            print(scr2ar)
            for k in reversed(sorted(scr2ar, key=lambda x: x[0])):
                parsedData.append({'score': k[0], 'name': k[1].name, 'text': k[1].text[0:220] + "(...)"})
        except Exception as e:
            print(e.with_traceback())
        return render(request, 'search.html', {'data': parsedData, 'q': {'fir': q}})
    return render(request, 'search.html', {'data': parsedData})


def data_load(request):
    if request.method == 'POST':
        load_data = request.POST.get('load_data')


def profile(request):
    from wikifinder.engine.data_loader import DataLoader
    import glob
    pathss = glob.glob("/home/przemek/Dokumenty/agh/projects/my-finder/myfinder/wikifinder/res/dumps/*xml*")

    dl = DataLoader(pathss[0])
    dl.load_xml_to_queue()
    dl.build_article()
    dl = None

    return HttpResponse('Hello World!')
