using Microsoft.TeamFoundation.MVVM;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Input;

namespace RTS_analysis
{
    public class MainViewModel:INotifyPropertyChanged
    {
        #region PropertyEvents

        public event PropertyChangedEventHandler PropertyChanged;
        protected bool SetField<ST>(ref ST field, ST value, string propertyName)
        {
            if (EqualityComparer<ST>.Default.Equals(field, value))
                return false;
            field = value;
            OnPropertyChanged(propertyName);
            return true;
        }
        private void OnPropertyChanged(string PropertyName)
        {
            var handler = PropertyChanged;
            if (handler != null)
                handler(this, new PropertyChangedEventArgs(PropertyName));
        }
        #endregion

        public MainViewModel()
        {
            _openFileDialog = new OpenFileDialog();
            _openFileDialog.Multiselect = true;
            Filenames = new ObservableCollection<string>();
            WorkingDirectory = Directory.GetCurrentDirectory();
        }

        private OpenFileDialog _openFileDialog;

        private DirectoryInfo _workingDirectory;
        public string WorkingDirectory
        {
            get { return _workingDirectory.FullName; }
            private set { SetField(ref _workingDirectory, new DirectoryInfo(value), "WorkingDirectory"); }

        }


        private ICommand _processCommand;

        public ICommand ProcessCommand
        {
            get { return _processCommand?? (_processCommand = new RelayCommand(()=>StartProcessing())); }
            set { _processCommand = value; }
        }

        private void StartProcessing()
        {

        }

        private void StartProcessing(string name)
        {

        }

        private void StopCurrent()
        {

        }

        private void StopAll()
        {

        }
 
        private ICommand _openFiles;
               
        public ICommand OpenFiles
        {
            get
            {
                return _openFiles ?? (_openFiles = new RelayCommand(() =>
                    {
                        _openFileDialog.ShowDialog();
                        _filenames.Clear();
                        for (int i = 0; i < _openFileDialog.FileNames.Length; i++)
                        {
                            System.IO.FileInfo fi = new System.IO.FileInfo(_openFileDialog.FileNames[i]);
                            Filenames.Add(fi.Name);
                        }
                        
                    }
                    ));
            }

        }

        private ObservableCollection<string> _filenames;

        public ObservableCollection<string> Filenames
        {
            get { return _filenames; }
            private set {
                SetField<ObservableCollection<string>>(ref _filenames, value, "Filenames");
            }
        }







     
    }
}
