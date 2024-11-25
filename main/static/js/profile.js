// Profile Picture Preview
const profilePictureInput = document.getElementById('profilePicture');
const avatarPreview = document.getElementById('avatarPreview');

profilePictureInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();

        reader.addEventListener('load', function () {
            avatarPreview.setAttribute('src', this.result);
        });

        reader.readAsDataURL(file);
    }
});