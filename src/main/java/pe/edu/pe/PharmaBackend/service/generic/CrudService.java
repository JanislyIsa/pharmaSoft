package pe.edu.pe.PharmaBackend.service.generic;

import java.util.Optional;

public interface CrudService <REQ, RES, ID>{
    RES create(REQ t);
    RES update(ID id, REQ t);
    Optional<RES> read(ID id);
    void delete(ID id);
    Iterable<RES> readAll();
}