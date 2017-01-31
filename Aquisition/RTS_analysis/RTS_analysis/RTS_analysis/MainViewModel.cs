using Microsoft.TeamFoundation.MVVM;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
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
            
            Filenames = new ObservableCollection<string>();
            WorkingDirectory = Directory.GetCurrentDirectory();
            _openFileDialog = new OpenFileDialog();
            //_openFileDialog.InitialDirectory = WorkingDirectory;
            _openFileDialog.Multiselect = true;
            _openFileDialog.Filter = "Data file(*.dat)|*.dat";
            _processingInProgress = false;
            _backgroundWorker = new BackgroundWorker();
            _backgroundWorker.WorkerReportsProgress = true;
            _backgroundWorker.WorkerSupportsCancellation = true;
            _backgroundWorker.DoWork += _backgroundWorker_DoWork;
            _backgroundWorker.ProgressChanged += _backgroundWorker_ProgressChanged;
            _backgroundWorker.RunWorkerCompleted += _backgroundWorker_RunWorkerCompleted;
            
        }

        
        private BackgroundWorker _backgroundWorker;

        private bool _processingInProgress;
        public bool ProcessingInProgress
        {
            get { return _processingInProgress; }
            private set 
            {
                SetField(ref _processingInProgress, value, "ProcessingInProgress");
            }
        }

        private OpenFileDialog _openFileDialog;

        private DirectoryInfo _workingDirectory;
        public string WorkingDirectory
        {
            get { return _workingDirectory.FullName; }
            private set { SetField(ref _workingDirectory, new DirectoryInfo(value), "WorkingDirectory"); }

        }

        private ICommand _openFiles;
        public ICommand OpenFiles
        {
            get
            {
                return _openFiles ?? (_openFiles = new RelayCommand((param) =>
                {
                    if (_openFileDialog.ShowDialog() != DialogResult.OK)
                        return;
                    
                    
                    //System.Diagnostics.Debug.Print(WorkingDirectory);
                    _filenames.Clear();
                    for (int i = 0; i < _openFileDialog.FileNames.Length; i++)
                    {
                        System.IO.FileInfo fi = new System.IO.FileInfo(_openFileDialog.FileNames[i]);
                        Filenames.Add(fi.FullName);
                    }

                },(param)=>
                    {
                        return !ProcessingInProgress;
                    }
                    ));
            }

        }

        private ObservableCollection<string> _filenames;

        public ObservableCollection<string> Filenames
        {
            get { return _filenames; }
            private set
            {
                SetField<ObservableCollection<string>>(ref _filenames, value, "Filenames");
            }
        }

        //private int _selectedFilename;

        //public int SelectedFilename
        //{
        //    get { return _selectedFilename;  }
        //    set {
        //        _selectedFilename = value; 
        //        System.Diagnostics.Debug.Print("{0}",_selectedFilename); 
        //    }
        //}

        private int _totalSampleNumber;

        public int TotalSampleNumber
        {
            get { return _totalSampleNumber; }
            set {
                SetField<int>(ref _totalSampleNumber, value, "TotalSampleNumber");
                //_totalSampleNumber = value;
                System.Diagnostics.Debug.Print("{0}", _totalSampleNumber); 
            }
        }

        private int _levelsNumber;

        public int LevelsNumber
        {
            get { return _levelsNumber; }
            set {
                SetField<int>(ref _levelsNumber, value, "LevelsNumber");
                //_levelsNumber = value;
                System.Diagnostics.Debug.Print("{0}", _levelsNumber); 
            }
        }


        private ICommand _processStartCommand;

        public ICommand ProcessStartCommand
        {
            get
            {
                return _processStartCommand ?? (_processStartCommand = new RelayCommand((param) =>
                {
                    StartProcessing();
                }, (param) =>
                {
                    return !ProcessingInProgress;
                }));
            } 
            private set { _processStartCommand = value; }
        }

        private void StartProcessing()
        {
            
            if (Filenames.Count == 0)
            {
                MessageBox.Show("Please select files for analysis");
            }
            else
            {
                ProcessingInProgress = true;
                System.Diagnostics.Debug.Print("start processing");
                _backgroundWorker.RunWorkerAsync();
            }
        }

        //private void StartProcessing(string name)
        //{

        //}

        private ICommand _stopCurrentProcessCommand;

        public ICommand StopCurrentProcessCommand
        {
            get
            {
                return _stopCurrentProcessCommand ?? (_stopCurrentProcessCommand = new RelayCommand((param) =>
                {
                    StopCurrent();
                }, (param) =>
                {
                    return false;
                }));
            }
            private set { _stopCurrentProcessCommand = value; }
        }

        private void StopCurrent()
        {
            System.Diagnostics.Debug.Print("stop current");
            _backgroundWorker.CancelAsync();
        }


        private ICommand _stopAllProcessCommands;

        public ICommand StopAllProcessCommands
        {
            get
            {
                return _stopAllProcessCommands ?? (_stopAllProcessCommands = new RelayCommand((param) =>
                {
                    StopAll();
                }, (param) =>
                {
                    return ProcessingInProgress;
                }));
            }
            private set { _stopAllProcessCommands = value; }
        }


        private void StopAll()
        {
            ProcessingInProgress = false;
            System.Diagnostics.Debug.Print("stop all");
            _backgroundWorker.CancelAsync();
            
        }




        private void _backgroundWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            ProcessingInProgress = false;
            ProgressPercentage = 0;
            MessageBox.Show("Calculations completed");
            //throw new NotImplementedException();
        }

        private int _progressPercantage;

        public int ProgressPercentage
        {
            get { return _progressPercantage; }
            set {
                SetField(ref _progressPercantage, value, "ProgressPercentage");
            }
        }

        private string _actionsLog;

        public string ActionsLog
        {
            get { return _actionsLog; }
            set { SetField(ref _actionsLog, value, "ActionLog"); }
        }

        private void AppendToLog(string text)
        {
            StringBuilder sb = new StringBuilder(ActionsLog);
            
            sb.AppendLine(text);
            _actionsLog = sb.ToString();
            OnPropertyChanged("ActionsLog");
            
        }

        private void _backgroundWorker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            ProgressPercentage = e.ProgressPercentage;
            string state = e.UserState.ToString();//String.Format("percentage completed: {0}\nstate:\n{1}\n",ProgressPercentage,e.UserState);
            
            AppendToLog(state);
            //throw new NotImplementedException();
        }

        private void _backgroundWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker worker = sender as BackgroundWorker;
            for (int i = 0; i < Filenames.Count; i++)
            {   
                if(worker.CancellationPending == true)
                {
                    e.Cancel = true;
                    break;
                }
                else
                {
                    ProcessStartInfo startInfo = new ProcessStartInfo();
                    startInfo.FileName = "python.exe";
                    startInfo.Arguments = String.Format("rts_new.py {0} @nsamples {1} @nlevels {2}", Filenames[i], TotalSampleNumber, LevelsNumber);
                    startInfo.UseShellExecute = false;
                    startInfo.RedirectStandardOutput = true;
                    startInfo.CreateNoWindow = true;
                    string state = String.Empty;
                    using (Process process = Process.Start(startInfo))
                    {
                        using (StreamReader reader = process.StandardOutput)
                        {
                            while (!reader.EndOfStream)
                            {
                                state = reader.ReadLine();
                                worker.ReportProgress((int)(i * 100.0 / Filenames.Count), state);
                                Debug.Print(state);
                            }
                        }
                    }

                }
            }
        }

        



     
    }
}
