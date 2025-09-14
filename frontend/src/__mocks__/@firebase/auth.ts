const auth = {
  currentUser: null,
  signInWithEmailAndPassword: jest.fn(),
  signInWithPopup: jest.fn(),
  signOut: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  updateProfile: jest.fn(),
  GoogleAuthProvider: jest.fn(),
  FacebookAuthProvider: jest.fn(),
  useDeviceLanguage: jest.fn()
};

export const getAuth = jest.fn(() => auth);
export const onAuthStateChanged = jest.fn((auth, callback) => {
  callback(null);
  return jest.fn(); // Return unsubscribe function
});