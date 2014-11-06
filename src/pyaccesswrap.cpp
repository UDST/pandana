#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#include "accessibility.h"
#include "graphalg.h"

std::vector<std::shared_ptr<MTC::accessibility::Accessibility> > sas;


static PyObject *
create_graphs(PyObject *self, PyObject *args) {
    int n;
	if (!PyArg_ParseTuple(args, "i", &n)) return NULL;
    for(int i=0;i<n;i++) {
        std::shared_ptr<MTC::accessibility::Accessibility>
            aptr(new MTC::accessibility::Accessibility);
        sas.push_back(aptr);
    }
    return Py_None;
}


static PyObject *
create_graph(PyObject *self, PyObject *args)
{
    int id, twoway;
	PyObject *input1, *input2, *input3, *input4;
	// this is node ids, node xys, edge ids, and edge weights
	if (!PyArg_ParseTuple(args, "iOOOOi", &id, &input1, &input2,
											&input3, &input4, &twoway))
											return NULL;

	PyArrayObject *pyo;
	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input1,
														NPY_INT32, 1, 1);
	if (pyo == NULL) return NULL;
    int *nodeids = (int*)PyArray_DATA(pyo);
    int numnodes = PyArray_DIMS(pyo)[0];

	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input2,
														NPY_FLOAT32, 2, 2);
	if (pyo == NULL) return NULL;
    float *nodexy = (float*)PyArray_DATA(pyo);
    assert(numnodes == PyArray_DIMS(pyo)[0]);
    assert(2 == PyArray_DIMS(pyo)[1]);

	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input3,
														NPY_INT32, 2, 2);
	if (pyo == NULL) return NULL;
    int *edges = (int*)PyArray_DATA(pyo);
    int numedges = PyArray_DIMS(pyo)[0];
    assert(2 == PyArray_DIMS(pyo)[1]);

	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input4,
														NPY_FLOAT32, 1, 2);
	if (pyo == NULL) return NULL;
    float *edgeweights = (float*)PyArray_DATA(pyo);
    int numimpedances = 1;
	if(PyArray_NDIM(pyo) == 1) assert(numedges == PyArray_DIMS(pyo)[0]);
    else {
        numimpedances = PyArray_DIMS(pyo)[0];
		assert(numedges == PyArray_DIMS(pyo)[1]);
	}

    if(id>=sas.size()) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[id];

    for(int i = 0 ; i < numimpedances ; i++) {
        std::shared_ptr<MTC::accessibility::Graphalg>
            ptr(new MTC::accessibility::Graphalg);
        sa->ga.push_back(ptr);
        sa->ga[i]->Build(nodeids, nodexy, numnodes, edges,
            edgeweights+(numedges*i), numedges, twoway);
    }

    sa->numnodes = sa->ga[0]->numnodes;

    Py_RETURN_NONE;
}


static PyObject *
initialize_pois(PyObject *self, PyObject *args)
{
    int nc, mi;
    double md;
	if (!PyArg_ParseTuple(args, "idi", &nc, &md, &mi)) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[0];

    sa->initializePOIs(nc,md,mi);

    Py_RETURN_NONE;
}


static PyObject *
initialize_category(PyObject *self, PyObject *args)
{
    int id;
	PyObject *input1;
	if (!PyArg_ParseTuple(args, "iO", &id, &input1)) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[0];

    PyArrayObject *pyo;
	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input1,
														NPY_FLOAT32, 2, 2);
	if (pyo == NULL) return NULL;
    float *pois = (float*)PyArray_DATA(pyo);
    int numpois = PyArray_DIMS(pyo)[0];
    assert(2 == PyArray_DIMS(pyo)[1]);

    MTC::accessibility::accessibility_vars_t av;
    av.resize(sa->numnodes);
    for(int i = 0 ; i < numpois ; i++) {
        // XXX this should really only respond to node ids and use the xy
		// conversion function below
        int nodeid = sa->ga[0]->NearestNode(pois[i*2+0],pois[i*2+1],NULL);
		//assert(nodeid < sa->ga[0].numpois);
        av[nodeid].push_back(nodeid);
    }

    sa->initializeCategory(id,av);

    Py_RETURN_NONE;
}


static PyObject *
find_all_nearest_pois(PyObject *self, PyObject *args)
{
    double radius;
	int varind, num, gno, impno;
	if (!PyArg_ParseTuple(args, "diiii", &radius, &num, &varind,
	                        &gno, &impno))
	    return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

    std::vector<std::vector<float> > nodes =
        sa->findAllNearestPOIs(radius, num, varind, impno);

	npy_intp dims[2];
	dims[0] = nodes.size();
	dims[1] = num;
    PyArrayObject *returnobj = (PyArrayObject *)PyArray_SimpleNew(2, dims,
															NPY_FLOAT);
    for(int i = 0 ; i < dims[0] ; i++) {
        for(int j = 0 ; j < dims[1] ; j++) {
            *(npy_float *) PyArray_GETPTR2(returnobj, i, j) = (npy_float) nodes[i][j];
        }
    }

	return PyArray_Return(returnobj);
}


static PyObject *
initialize_acc_vars(PyObject *self, PyObject *args)
{
    int gno, nc;
	if (!PyArg_ParseTuple(args, "ii", &gno, &nc)) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

    sa->initializeAccVars(nc);

    Py_RETURN_NONE;
}


static PyObject *
initialize_acc_var(PyObject *self, PyObject *args)
{
    int gno, id;
	PyObject *input1, *input2;
	if (!PyArg_ParseTuple(args, "iiOO", &gno, &id, &input1, &input2))
	    return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

	PyArrayObject *pyo;
	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input1,
														NPY_INT32, 1, 1);
	if (pyo == NULL) return NULL;
    int *nodeids = (int*)PyArray_DATA(pyo);
    int num = PyArray_DIMS(pyo)[0];

	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input2,
														NPY_FLOAT32, 1, 1);
	if (pyo == NULL) return NULL;
    float *accvars = (float*)PyArray_DATA(pyo);
    assert(num == PyArray_DIMS(pyo)[0]);

    MTC::accessibility::accessibility_vars_t av;
    av.resize(sa->numnodes);

    int cnt = 0;
    for(int i = 0 ; i < num ; i++) {
        if(nodeids[i] == -1) {
             cnt++;
             continue;
        }
        av[nodeids[i]].push_back(accvars[i]);
    }

    sa->initializeAccVar(id,av);

    Py_RETURN_NONE;
}


static PyObject *
get_all_aggregate_accessibility_variables(PyObject *self, PyObject *args)
{

    double radius;
	int varind, aggtyp, decay, graphno, impno;
	if (!PyArg_ParseTuple(args, "diiiii", &radius, &varind, &aggtyp, &decay,
															&graphno, &impno))
																return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[graphno];


    std::vector<double> nodes = sa->getAllAggregateAccessibilityVariables(
                                radius,
								varind,
								(MTC::accessibility::aggregation_types_t)aggtyp,
								(MTC::accessibility::decay_func_t)decay,
								impno);
    npy_intp len = nodes.size();
    PyArrayObject *returnobj = (PyArrayObject *)PyArray_SimpleNew(1, &len,
															NPY_FLOAT32);
    for(int i = 0 ; i < len ; i++) ((float*)PyArray_DATA(returnobj))[i] =
															(float)nodes[i];

	return PyArray_Return(returnobj);
}


static PyObject *
xy_to_node(PyObject *self, PyObject *args)
{
	PyObject *input1;
    double distance;
    int gno;

	if (!PyArg_ParseTuple(args, "Odi", &input1, &distance, &gno)) return NULL;
    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

	PyArrayObject *pyo;
	pyo = (PyArrayObject*)PyArray_ContiguousFromObject(input1,
														NPY_FLOAT32, 2, 2);
	if (pyo == NULL) return NULL;
    float *xys = (float*)PyArray_DATA(pyo);
    npy_intp num = PyArray_DIMS(pyo)[0];
    assert(2 == PyArray_DIMS(pyo)[1]);

	PyArrayObject *returnobj = (PyArrayObject *)PyArray_SimpleNew(1, &num,
	    NPY_INT32);
    int *nodes = (int*)PyArray_DATA(returnobj);

    //#pragma omp parallel for
    for(int i = 0 ; i < num ; i++) {
        double d;
		// now that we have multiple subgraphs, the nearest neighbor should
		// really be moved to the accessibility object
		int nodeid = sa->ga[0]->NearestNode(xys[i*2+0],xys[i*2+1],&d);
        if(distance != -1.0 && d > distance) {
            nodes[i] = -1;
            continue;
        }
        nodes[i] = nodeid;
    }
	return PyArray_Return(returnobj);
}


static PyObject *
get_nodes_in_range(PyObject *self, PyObject *args)
{
    double radius;
    int nodeid, gno, impno;
	if (!PyArg_ParseTuple(args, "idii", &nodeid, &radius, &gno, &impno))
																return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

    MTC::accessibility::DistanceVec dm = sa->Range(nodeid,radius,impno);
    npy_intp num = dm.size();
    PyArrayObject *nodes = (PyArrayObject *)PyArray_SimpleNew(1, &num,
															NPY_INT32);
    PyArrayObject *dists = (PyArrayObject *)PyArray_SimpleNew(1, &num,
															NPY_FLOAT32);
    for(int i = 0 ; i < num ; i++) {
        ((int*)PyArray_DATA(nodes))[i] = dm[i].first;
        ((float*)PyArray_DATA(dists))[i] = dm[i].second;
    }

    PyObject *returnobj = Py_BuildValue("(OO)",nodes,dists);
    return returnobj;
}


PyObject *sample_nodes(int *inodes, int inumnodes, int samplesize,
    double radius, int *skipnodeids, int gno, int impno) {

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

	npy_intp num = sa->numnodes;
    // if nodes is not null we do have a list of nodeids
    if(inodes) num = inumnodes;

    npy_intp dims[2];
    dims[0] = num;
    dims[1] = samplesize;
    PyArrayObject *nodes = (PyArrayObject *)PyArray_SimpleNew(2, dims,
															NPY_INT32);
    PyArrayObject *numnodes = (PyArrayObject *)PyArray_SimpleNew(1, &num,
															NPY_INT32);
    PyArrayObject *dists = (PyArrayObject *)PyArray_SimpleNew(2, dims,
															NPY_FLOAT32);
    int nodeid;
    #pragma omp parallel for
    for(int i = 0 ; i < num ; i++) {
        if(inodes) nodeid = inodes[i];
        else nodeid = i;

        MTC::accessibility::DistanceVec dm = sa->Range(nodeid,radius,impno);
        int num = dm.size();
        ((int*)PyArray_DATA(numnodes))[i] = num;
        std::random_shuffle(dm.begin(),dm.end());
        for(int j = 0, skipped = 0 ; j < samplesize+skipped ; j++) {

            // skip the chosen nodeid if we find it
           if(skipnodeids && skipnodeids[i] != -1 && j < dm.size() &&
              skipnodeids[i] == dm[j].first) {
                skipped++;
                continue;
            }

            if(j >= dm.size()) {
                ((int*)PyArray_DATA(nodes))[i*samplesize+j-skipped] = -1;
                ((float*)PyArray_DATA(dists))[i*samplesize+j-skipped] = -1.0;
                continue;
            }

            ((int*)PyArray_DATA(nodes))[i*samplesize+j-skipped] =
                dm[j].first;
            ((float*)PyArray_DATA(dists))[i*samplesize+j-skipped] =
                dm[j].second;
        }
    }

    PyObject *returnobj = Py_BuildValue("(OOO)",numnodes,nodes,dists);
    return returnobj;
}


/* this function samples a certain number of nodes from the available range
   for a given graph */
static PyObject *
sample_all_nodes_in_range(PyObject *self, PyObject *args)
{
    double radius;
    int samplesize, gno, impno;
	if (!PyArg_ParseTuple(args, "idii", &samplesize, &radius, &gno, &impno))
																return NULL;
    return sample_nodes(NULL,-1,samplesize,radius,NULL,gno,impno);
}


static PyObject *
get_all_model_results(PyObject *self, PyObject *args)
{

    double radius, asc, denom, nestdenom, mu, distcoeff;
	int graphno, impno, numvars;
	PyObject *input1, *input2;
	if (!PyArg_ParseTuple(args, "dOOdddddii", &radius, &input1, &input2,
	    &distcoeff, &asc, &denom, &nestdenom, &mu, &graphno, &impno))
		    return NULL;

	PyArrayObject *pyo1, *pyo2;
	pyo1 = (PyArrayObject*)PyArray_ContiguousFromObject(input1,
														NPY_INT32, 1, 1);
    if(pyo1==NULL) return NULL;
    int *varindexes = (int*)PyArray_DATA(pyo1);
    npy_intp num = PyArray_DIMS(pyo1)[0];

	pyo2 = (PyArrayObject*)PyArray_ContiguousFromObject(input2,
														NPY_FLOAT32, 1, 1);
    if(pyo2==NULL) return NULL;
    float *varcoeffs = (float*)PyArray_DATA(pyo2);
    npy_intp num2 = PyArray_DIMS(pyo2)[0];

    if(num != num2) return NULL;
    else numvars = num;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[graphno];

    std::vector<double> nodes = sa->getAllModelResults(radius, numvars,
        varindexes, varcoeffs, distcoeff, asc, denom, nestdenom, mu, impno);

    npy_intp len = nodes.size();

    PyArrayObject *returnobj = (PyArrayObject *)PyArray_SimpleNew(1, &len,
															NPY_FLOAT32);

    for(int i = 0 ; i < len ; i++) ((float*)PyArray_DATA(returnobj))[i] =
															(float)nodes[i];

	return PyArray_Return(returnobj);
}


static PyObject *
compute_all_design_variables(PyObject *self, PyObject *args)
{
    double radius;
	const char *type;
    int gno;
	if (!PyArg_ParseTuple(args, "dsi", &radius, &type, &gno)) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

	npy_intp num = sa->numnodes;
	PyArrayObject *returnobj = (PyArrayObject *)PyArray_SimpleNew(1,
	    &num, NPY_FLOAT32);
    float *nodes = (float*)PyArray_DATA(returnobj);

    std::string str(type);

    #pragma omp parallel for
    for(int i = 0 ; i < num ; i++) {
    	nodes[i] = (float)sa->computeDesignVariable(i,radius,str);
    }

	return PyArray_Return(returnobj);
}


static PyObject *
precompute_range(PyObject *self, PyObject *args)
{
    int gno;
    double radius;
	if (!PyArg_ParseTuple(args, "di", &radius, &gno)) return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

	sa->precomputeRangeQueries((float)radius);

	Py_RETURN_NONE;
}


static PyObject *
route_distance(PyObject *self, PyObject *args)
{
    int gno, impno, srcnode, destnode;
	if (!PyArg_ParseTuple(args, "iiii", &srcnode, &destnode, &gno, &impno))
	    return NULL;

    std::shared_ptr<MTC::accessibility::Accessibility> sa = sas[gno];

    double dist = sa->ga[impno]->Distance(srcnode,destnode);

    return PyFloat_FromDouble(dist);
}


static PyMethodDef myMethods[] = {
    /*{"route_distance", route_distance, METH_VARARGS, "route_distance"},*/
    {"create_graphs", create_graphs, METH_VARARGS, "create_graphs"},
    {"create_graph", create_graph, METH_VARARGS, "create_graph"},
    /*{"get_nodes_in_range", get_nodes_in_range, METH_VARARGS,
        "get_nodes_in_range"},
    {"sample_all_nodes_in_range", sample_all_nodes_in_range, METH_VARARGS,
        "sample_all_nodes_in_range"},*/
    {"initialize_pois", initialize_pois, METH_VARARGS, "initialize_pois"},
    {"initialize_category", initialize_category, METH_VARARGS,
        "initialize_category"},
    {"find_all_nearest_pois", find_all_nearest_pois, METH_VARARGS,
        "find_all_nearest_pois"},
    /*{"get_all_model_results", get_all_model_results, METH_VARARGS,
    "get_all_model_results"},*/
    {"get_all_aggregate_accessibility_variables",
        get_all_aggregate_accessibility_variables, METH_VARARGS,
        "get_all_aggregate_accessibility_variables"},
	/*{"compute_all_design_variables", compute_all_design_variables,
	    METH_VARARGS, "compute_all_design_variables"},*/
    {"initialize_acc_var", initialize_acc_var, METH_VARARGS,
        "initialize_acc_var"},
    {"initialize_acc_vars", initialize_acc_vars, METH_VARARGS,
        "initialize_acc_vars"},
    {"xy_to_node", xy_to_node, METH_VARARGS, "xy_to_node"},
	{"precompute_range", precompute_range, METH_VARARGS, "precompute_range"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC init_pyaccess(void)
{
	PyObject *m=Py_InitModule("_pyaccess", myMethods);
	import_array();
	PyObject *pyError = PyErr_NewException((char*)"pyaccess.error", NULL, NULL);
    Py_INCREF(pyError);
    PyModule_AddObject(m, "error", pyError);
}
