#include <Python.h>
#include <structmember.h>

#include <numpy/arrayobject.h>

static PyObject *SpamError;

typedef struct {
  PyArrayObject base;
  PyDictObject* unit;
  /* new things here */
} UnitArrayObject;

PyTypeObject unitArrayObjectType;

static PyObject*
mulunit(PyObject *unit1, PyObject *unit2) {
	PyObject *u = NULL;
	u = PyDict_Copy(unit1);

	PyObject *key = NULL, *value = NULL, *e = NULL;
	Py_ssize_t pos = 0;

	while (PyDict_Next(unit2, &pos, &key, &value)) {
	    /* do something interesting with the values... */
		if (PyDict_Contains(u, key)) {
			Py_XDECREF(e);
			e = PyNumber_Subtract(value, PyDict_GetItem(u, key));
			if (PyObject_IsTrue(e) != 0) {
				PyDict_SetItem(u, key, e);
			} else {
				PyDict_DelItem(u, key);
			}
		} else if (PyObject_IsTrue(value)) {
			PyDict_SetItem(u, key, PyNumber_Negative(value));
		}
	}
	Py_XDECREF(e);
    return u;
	
}

static PyObject *
divunit(PyObject *unit1, PyObject *unit2) {
    PyObject *u;

	u = PyDict_Copy(unit1);

	PyObject *key = NULL, *value = NULL, *e = NULL;
	Py_ssize_t pos = 0;

	while (PyDict_Next(unit2, &pos, &key, &value)) {
	    /* do something interesting with the values... */
		if (PyDict_Contains(u, key)) {
			Py_XDECREF(e);
			e = PyNumber_Subtract(value, PyDict_GetItem(u, key));
			if (PyObject_IsTrue(e) != 0) {
				PyDict_SetItem(u, key, e);
			} else {
				PyDict_DelItem(u, key);
			}
		} else if (PyObject_IsTrue(value)) {
			PyDict_SetItem(u, key, PyNumber_Negative(value));
		}
	}
	Py_XDECREF(e);

	return u;
}
static PyObject* formatunit(PyObject*);

static PyObject*
py_formatunit(PyObject* self, PyObject* args) {
  PyObject *arg1 = NULL;
  if (!PyArg_ParseTuple(args, "O", &arg1)) {return NULL;}
  return formatunit(arg1);
}

static PyObject*
formatunit(PyObject *unit) {
    PyObject *nom = NULL;
    PyObject *denom = NULL;
    PyObject *key = NULL, *value = NULL;
    PyObject *null = NULL, *one = NULL, *minusone = NULL;
    PyObject *tmp = NULL, *expFormat = NULL, *format = NULL;
    int d = 0, n = 0;
    Py_ssize_t i = 0;
    
    null = Py_BuildValue("i", 0);
    one = Py_BuildValue("i", 1);
    minusone = Py_BuildValue("i",-1);
    nom = PyString_FromString("");
    denom = PyString_FromString("");
    expFormat = PyString_FromString("%s**%s ");
    format = PyString_FromString("%s ");
    
    while(PyDict_Next(unit, &i, &key, &value)) {
    	if (PyObject_Compare(value, null)==1) {
    		n++;
    		if (PyObject_Compare(value, one) != 0) {
            	//format with exponent
            	tmp = PyNumber_Absolute(value);
              PyString_ConcatAndDel(&nom, PyString_Format(expFormat, 
          		Py_BuildValue("(OO)",key, tmp)));
              Py_XDECREF(tmp);
            }
            else {
            	//format without exponent
            	PyString_ConcatAndDel(&nom, PyString_Format(format, key));
            }
    	}
        else {
			d++;
        	if (PyObject_Compare(value, minusone) != 0) {
				tmp = PyNumber_Absolute(value);
        		PyString_ConcatAndDel(&denom, PyString_Format(expFormat, 
        				Py_BuildValue("(OO)",key, tmp)));
        		Py_XDECREF(tmp);
        	} else {
            	//format without exponent
            	PyString_ConcatAndDel(&denom, PyString_Format(format, key));        		
        	}
        }
    }
    if (n > 0) {
    	_PyString_Resize(&nom, PyObject_Length(nom)-1);
    	tmp = nom;
    } else {
    	tmp = Py_BuildValue("s", "1");
    	Py_XDECREF(nom);
    }
    if (d > 0) {
        PyString_ConcatAndDel(&tmp, PyString_FromString("/"));
        _PyString_Resize(&denom, PyObject_Length(denom)-1);
        PyString_Concat(&tmp, denom);
    }
    Py_XDECREF(denom);
    
    Py_XDECREF(null);
    Py_XDECREF(one);
    Py_XDECREF(minusone);
    Py_XDECREF(expFormat);
    Py_XDECREF(format);
    
    return tmp;
fail:
    Py_XDECREF(nom);
    Py_XDECREF(denom);
    Py_XDECREF(null);
    Py_XDECREF(one);
    Py_XDECREF(minusone);
    Py_XDECREF(expFormat);
    Py_XDECREF(format);
    
    return NULL;
}

static PyObject*
powunit(PyObject *unit, PyObject* exponent) {
	Py_ssize_t i = 0;
	PyObject *key = NULL, *value = NULL, *res = NULL,
			*tmp = NULL;
	res = PyDict_New();
	while (PyDict_Next(unit, &i, &key, &value)) {
		tmp = PyNumber_Multiply(value, exponent);
		PyDict_SetItem(res, key, tmp);
		Py_XDECREF(tmp);
	}
	return res;
}

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

	//printf("hallo\n");
	if (!PyArg_ParseTuple(args, "OO|O&", &data, &unit, PyArray_DescrConverter, &dtype)) {
		Py_XDECREF(dtype);
    //TODO: raise exception?
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
      printf("incompatibel units in cast");

			//TODO: raise exception
			return NULL;
		}
	} else {
		if (PyObject_IsTrue(unit)) {
      //printf("before %p\n",res);
      tmp = res;
			res = PyArray_View((PyArrayObject*)res, NULL, &unitArrayObjectType);
			//printf("after %p unit %p\n", res, unit);
      if (tmp!=res) {
        Py_XDECREF(tmp);
      }
      ((UnitArrayObject*)res)->unit = (PyDictObject*)unit;
      Py_INCREF(unit);
      if (unit!=NULL) {
        printf("new unit: %s\n",PyString_AsString(PyObject_Str(unit)));
      }
		}
	}
  //printf("krass");
	return res;
}

static PyObject*
unitArray__array_finalize__(PyObject* new, PyObject* args) {
	PyObject *attr = NULL, *tmp = NULL;
  PyObject *parent = NULL;

  // #init the new unit to NULL (otherwise)
  // ((UnitArrayObject*)new)->unit = NULL;

  if (!PyArg_ParseTuple(args, "O", &parent)) {
    return NULL;
  }
	//printf("finalize parent: %p, new: %p\n", parent, new);
  //printf("finalize parent: %s\n",PyString_AsString(PyObject_Str(parent)));
   if (parent!=NULL) {
     printf("finalize parent %p\n", parent);
     attr = PyObject_GetAttrString(parent, "unit");
     printf("finalize get unit attr %p\n",attr);
     if (attr == NULL) {
        //parent has no 'unit' so we make a new empty one
       attr = PyDict_New();
       PyErr_Clear();
     }
   } 
   //Py_XINCREF(attr) 
  tmp = (PyObject*)((UnitArrayObject*)new)->unit;
  printf("finalize new.unit:%p tmp:%p attr:%p\n",((UnitArrayObject*)new)->unit, tmp, attr);
    //printf("finalize from unit");
    ((UnitArrayObject*)new)->unit = (PyDictObject*)attr;
      // if ((attr!=tmp)) {
      //   Py_XDECREF(tmp);
      // }

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
  //{"__array_finalize__", unitArray__array_finalize__, METH_VARARGS, "array finalize method"},
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
     {"mulunit", mulunit, METH_VARARGS,
      "process unit dictionary for multiplication"},
     {"formatunit", py_formatunit, METH_VARARGS,
      "process unit dictionary for multiplication"},
     // {"divunit", py_divunit, METH_VARARGS,
     //  "process unit dictionary for multiplication"},
     // {"powunit", powunit, METH_VARARGS,
     //  "process unit dictionary for multiplication"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyObject *unitArray = NULL;
PyMODINIT_FUNC
initspam(void)
{
  import_array();

  PyObject *m;

  Py_INCREF(&PyArray_Type);
  unitArrayObjectType.tp_base = &PyArray_Type;

  if (PyType_Ready(&unitArrayObjectType) < 0)
    return;


  m = Py_InitModule3("spam", SpamMethods, "some tests and a array type with units.");
  if (m == NULL)
    return;

  SpamError = PyErr_NewException("spam.error", NULL, NULL);
  Py_INCREF(SpamError);
  PyModule_AddObject(m, "error", SpamError);
  Py_INCREF(&unitArrayObjectType);
  PyModule_AddObject(m, "UnitArray", (PyObject *)&unitArrayObjectType);
  (void) Py_InitModule("spam", SpamMethods);

}

