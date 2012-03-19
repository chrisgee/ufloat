#include <Python.h>
#include <structmember.h>

#include <numpy/arrayobject.h>

static PyObject *SpamError;

typedef struct {
  PyArrayObject base;
  PyDictObject* unit;
} UnitArrayObject;

PyTypeObject unitArrayObjectType;

static int
checkunit(PyObject *unit1, PyObject *unit2) {
  return PyObject_Compare(unit1, unit2);
}

static PyObject *
unitArray_new(PyTypeObject *cls, PyObject *args, PyObject *kwargs) {
	PyObject *data = NULL,
			 *unit = NULL;
  PyArray_Descr* dtype = NULL;
  PyObject *res = NULL, *tmp = NULL;

	if (!PyArg_ParseTuple(args, "OO|O&", &data, &unit, PyArray_DescrConverter, &dtype)) {
		Py_XDECREF(dtype);
		return NULL;
	}
  
  res = PyArray_FromAny(data, dtype, 0, 0, NPY_ENSURECOPY, NULL);
	if (res == NULL) {
		Py_XDECREF(dtype);
    //TODO: raise exception?
		return NULL;
	}

	if (PyObject_IsInstance(data, (PyObject*)cls)) {
		if (unit!=NULL && !checkunit((PyObject*)((UnitArrayObject*)data)->unit,unit)) {
			Py_XDECREF(res);
 			//TODO: raise exception
			return NULL;
		}
	} else {
		if (PyObject_IsTrue(unit)) {
      tmp = res;
			res = PyArray_View((PyArrayObject*)res, NULL, &unitArrayObjectType);
      if (tmp!=res) {
        Py_XDECREF(tmp);
      }
      ((UnitArrayObject*)res)->unit = (PyDictObject*)unit;
      Py_INCREF(unit);
      if (unit!=NULL) {
      }
		}
	}
	return res;
}

static PyObject*
unitArray__array_finalize__(PyObject* new, PyObject* args) {
	PyObject *attr = NULL, *tmp = NULL;
  PyObject *parent = NULL;

  if (!PyArg_ParseTuple(args, "O", &parent)) {
    return NULL;
  }
   if (parent!=NULL) {
     attr = PyObject_GetAttrString(parent, "unit");
     if (attr == NULL) {
        //parent has no 'unit' so we make a new empty one
       attr = PyDict_New();
       PyErr_Clear();
     }
   } 
  tmp = (PyObject*)((UnitArrayObject*)new)->unit;
    ((UnitArrayObject*)new)->unit = (PyDictObject*)attr;

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* 
unitArray__array_wrap__(PyObject *self, PyObject *args) {
	PyObject *array = NULL, *context = NULL;
	
	if (!PyArg_ParseTuple(args, "OO", array, context)) {
		//TODO: raise exception
		return NULL;
	}
	
	printf("%s",PyString_AsString(PyObject_Str(context)));
	
  Py_INCREF(array);
  return array;
}


static PyMethodDef unitArrayMethods[] = {
  {"__array_finalize__", unitArray__array_finalize__, METH_VARARGS, "array finalize method"},
  {"__array_wrap__", unitArray__array_wrap__, METH_VARARGS, "array wrap method"},
  {NULL, NULL, 0, NULL}
};

static PyMemberDef unitArrayMembers[] = {
  {"unit", T_OBJECT, offsetof(UnitArrayObject, unit),  0, "dictionary containing unit info."},
  {NULL, 0, 0, 0, NULL}
};

PyTypeObject unitArrayObjectType = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size        */
	"spam.UnitArray",		/* tp_name        */
	sizeof(UnitArrayObject),		/* tp_basicsize   */
	0,				/* tp_itemsize    */
	0,				/* tp_dealloc     */
	0,				/* tp_print       */
	0,				/* tp_getattr     */
	0,				/* tp_setattr     */
	0,				/* tp_compare     */
	0,				/* tp_repr        */
	0,				/* tp_as_number   */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping  */
	0,				/* tp_hash        */
	0,				/* tp_call        */
	0,				/* tp_str         */
	0,				/* tp_getattro    */
	0,				/* tp_setattro    */
	0,				/* tp_as_buffer   */
	Py_TPFLAGS_DEFAULT,		/* tp_flags       */
	"A numpy array with units",	/* tp_doc         */
  0,        /* traverseproc */
  0,        /* tp_clear*/
  0,        /* tp_richcompare */
  0,        /* tp_weaklistoffset */
  0,        /* tp_iter */
  0,        /* tp_iternext */
  unitArrayMethods,        /* tp_methods */
  unitArrayMembers,        /* tp_members */
  0,        /* tp_getset */
  0,        /* tp_base*/
  0,        /* tp_dict */
  0,        /* tp_descr_get*/
  0,        /* tp_descr_set */
  0,        /* tp_dictoffset */
  0,        /* tp_init */
  0,        /* tp_alloc */
  unitArray_new /* tp_new */
};


static PyMethodDef SpamMethods[] = {
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyObject *unitArray = NULL;
PyMODINIT_FUNC
initspampub(void)
{
  import_array();

  PyObject *m;

  Py_INCREF(&PyArray_Type);
  unitArrayObjectType.tp_base = &PyArray_Type;

  if (PyType_Ready(&unitArrayObjectType) < 0)
    return;


  m = Py_InitModule3("spampub", SpamMethods, "some tests and a array type with units.");
  if (m == NULL)
    return;

  SpamError = PyErr_NewException("spampub.error", NULL, NULL);
  Py_INCREF(SpamError);
  PyModule_AddObject(m, "error", SpamError);
  Py_INCREF(&unitArrayObjectType);
  PyModule_AddObject(m, "UnitArray", (PyObject *)&unitArrayObjectType);
  (void) Py_InitModule("spampub", SpamMethods);

}

