const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp();

exports.disableUserAuth = functions.https.onCall(async (data, context) => {
  // Verificar si el usuario que realiza la llamada está autenticado
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'Usuario no autenticado');
  }

  // Obtener información del usuario que realiza la llamada
  const callerUid = context.auth.uid;
  const callerDoc = await admin.firestore().collection('users').doc(callerUid).get();
  
  // Verificar si es administrador
  if (!callerDoc.exists || callerDoc.data().role !== 'admin') {
    throw new functions.https.HttpsError('permission-denied', 'No tienes permisos para realizar esta acción');
  }

  try {
    const { uid, disabled } = data;
    
    // Actualizar el estado en Firebase Authentication
    await admin.auth().updateUser(uid, {
      disabled: disabled
    });
    
    return { success: true };
  } catch (error) {
    console.error('Error al deshabilitar usuario:', error);
    throw new functions.https.HttpsError('internal', 'Error al deshabilitar usuario', error.message);
  }
});